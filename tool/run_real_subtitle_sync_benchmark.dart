import 'dart:io';

import 'package:path/path.dart' as p;
import 'package:uuid/uuid.dart';
import 'package:flutter/widgets.dart';

import 'package:asr_tools/models/asr_project.dart';
import 'package:asr_tools/models/media_file.dart';
import 'package:asr_tools/models/subtitle_file.dart';
import 'package:asr_tools/models/timeline_data.dart';
import 'package:asr_tools/services/app_data_service.dart';
import 'package:asr_tools/services/audio_align_service.dart';
import 'package:asr_tools/services/database_service.dart';
import 'package:asr_tools/services/export_service.dart';
import 'package:asr_tools/services/ffmpeg_service.dart';
import 'package:asr_tools/services/media_scan_service.dart';
import 'package:asr_tools/services/subtitle_match_service.dart';
import 'package:asr_tools/services/subtitle_prepare_service.dart';

const _videoDir = r'G:\data\260224-元数据脚本测试\1_Video\220822shipin';
const _audioDir = r'G:\data\260224-元数据脚本测试\2_Audio\220822yinpin';
const _subtitleDir = r'G:\data\260224-元数据脚本测试\3_srt';
const _defaultVideoSrt = r'G:\data\260224-元数据脚本测试\3_srt\0916视频字幕.srt';
const _defaultAudioSrt = r'G:\data\260224-元数据脚本测试\3_srt\0916音频字幕.srt';
const _ffmpegDir = r'G:\data\app\DIT\ffmpeg';
const _outputDir = r'G:\data\app\ASR-tools\测试合板';
const _projectNamePrefix = 'real-subtitle-sync-benchmark';

Future<void> main([List<String> args = const []]) async {
  WidgetsFlutterBinding.ensureInitialized();
  final videoSrt = _readStringOption(args, 'video-srt') ?? _defaultVideoSrt;
  final audioSrt = _readStringOption(args, 'audio-srt') ?? _defaultAudioSrt;
  AppDataService.debugOverrideDirectories(
    executableDir: r'G:\data\app\ASR-tools\output\benchmark-runtime',
    legacySettingsDir: r'G:\data\app\ASR-tools\output\benchmark-runtime\legacy_settings',
    legacyDatabaseDir: r'G:\data\app\ASR-tools\output\benchmark-runtime\legacy_database',
  );
  final totalWatch = Stopwatch()..start();
  FfmpegService.setFfmpegDir(_ffmpegDir);
  await DatabaseService.init();
  await _cleanupProjects();

  final project = await _createProject();
  stdout.writeln('项目已创建: ${project.id}');

  final importWatch = Stopwatch()..start();
  final videoCount = await _importDirectory(
    project.id,
    _videoDir,
    MediaType.video,
  );
  final audioCount = await _importDirectory(
    project.id,
    _audioDir,
    MediaType.audio,
  );
  await _insertSubtitleFiles(project.id, videoSrt: videoSrt, audioSrt: audioSrt);
  importWatch.stop();
  stdout.writeln(
    '导入完成: 视频=$videoCount 音频=$audioCount 用时=${importWatch.elapsed}',
  );

  final prepareWatch = Stopwatch()..start();
  final summary = await SubtitlePrepareService.prepareProject(project.id);
  prepareWatch.stop();
  stdout.writeln(
    '字幕准备完成: cues=${summary.generatedSubtitleClips} windows=${summary.generatedWindows} 用时=${prepareWatch.elapsed}',
  );

  final matchWatch = Stopwatch()..start();
  final results = await SubtitleMatchService.matchProject(
    projectId: project.id,
    onProgress: (update) {
      stdout.writeln(
        '[MATCH] ${update.stage} ${update.current}/${update.total} '
        '${update.currentVideo ?? ''} ${(update.progress * 100).toStringAsFixed(1)}%',
      );
    },
  );
  matchWatch.stop();
  stdout.writeln('一键合板完成: results=${results.length} 用时=${matchWatch.elapsed}');

  final timelineWatch = Stopwatch()..start();
  final timeline = await AudioAlignService.buildTimeline(project.id);
  timelineWatch.stop();
  stdout.writeln(
    '时间线构建完成: clips=${timeline.length} 用时=${timelineWatch.elapsed}',
  );

  final exportBase = p.join(_outputDir, '220822_real_sync_benchmark');
  await ExportService.exportXmeml(
    timeline,
    '$exportBase.xml',
    preset: ExportPreset.review,
  );
  await ExportService.exportFcpxml(
    timeline,
    '$exportBase.fcpxml',
    preset: ExportPreset.review,
  );
  await ExportService.exportCsvReport(timeline, '$exportBase.csv');
  await File('$exportBase.segments.txt').writeAsString(
    _buildSegmentSummary(timeline),
  );

  totalWatch.stop();
  stdout.writeln('总耗时: ${totalWatch.elapsed}');
  stdout.writeln('已导出: $exportBase.xml');
  stdout.writeln('已导出: $exportBase.fcpxml');
  stdout.writeln('已导出: $exportBase.csv');
  stdout.writeln('已导出: $exportBase.segments.txt');
}

Future<void> _cleanupProjects() async {
  final projects = await DatabaseService.getAllProjects();
  for (final project in projects.where(
    (item) => item.name.startsWith(_projectNamePrefix),
  )) {
    await DatabaseService.deleteProject(project.id);
  }
}

Future<AsrProject> _createProject() async {
  final now = DateTime.now();
  final project = AsrProject(
    id: const Uuid().v4(),
    name: '$_projectNamePrefix-${now.millisecondsSinceEpoch}',
    videoDirectory: _videoDir,
    audioDirectory: _audioDir,
    status: ProjectStatus.imported,
    createdAt: now,
    updatedAt: now,
  );
  await DatabaseService.insertProject(project);
  return project;
}

Future<int> _importDirectory(
  String projectId,
  String dirPath,
  MediaType type,
) async {
  final files = await MediaScanService.scanDirectory(dirPath, type);
  final now = DateTime.now();
  for (var index = 0; index < files.length; index++) {
    final file = files[index];
    final info = await FfmpegService.probeMedia(file.path);
    await DatabaseService.insertMediaFile(
      MediaFile(
        id: const Uuid().v4(),
        projectId: projectId,
        filePath: file.path,
        type: type,
        durationMs: info.durationMs,
        sortIndex: index,
        frameRate: info.frameRate,
        sampleRate: info.sampleRate,
        channels: info.channels,
        width: info.width,
        height: info.height,
        hasEmbeddedAudio: info.hasEmbeddedAudio,
        fileSize: info.fileSize,
        modifiedAtMs: info.modifiedAtMs,
        createdAt: now,
      ),
    );
  }
  return files.length;
}

Future<void> _insertSubtitleFiles(
  String projectId, {
  required String videoSrt,
  required String audioSrt,
}) async {
  final now = DateTime.now();
  await DatabaseService.insertSubtitleFile(
    SubtitleFile(
      id: const Uuid().v4(),
      projectId: projectId,
      filePath: videoSrt,
      mediaType: MediaType.video,
      sourceType: SubtitleSourceType.aggregate,
      createdAt: now,
    ),
  );
  await DatabaseService.insertSubtitleFile(
    SubtitleFile(
      id: const Uuid().v4(),
      projectId: projectId,
      filePath: audioSrt,
      mediaType: MediaType.audio,
      sourceType: SubtitleSourceType.aggregate,
      createdAt: now,
    ),
  );
}

String? _readStringOption(List<String> args, String name) {
  final inlinePrefix = '--$name=';
  for (int i = 0; i < args.length; i++) {
    final arg = args[i];
    if (arg.startsWith(inlinePrefix)) {
      return arg.substring(inlinePrefix.length);
    }
    if (arg == '--$name' && i + 1 < args.length) {
      return args[i + 1];
    }
  }
  return null;
}

String _buildSegmentSummary(List<TimelineData> timeline) {
  final buffer = StringBuffer();
  for (final item in timeline) {
    buffer.writeln('${item.videoFileName} | status=${item.status} | segments=${item.segmentCount}');
    for (final segment in item.segments) {
      buffer.writeln(
        '  S${segment.segmentIndex + 1} ${segment.audioFileName} | '
        'video=${segment.videoStartMs}-${segment.videoEndMs} | '
        'audio=${segment.audioSourceInMs}-${segment.audioSourceOutMs} | '
        'offset=${segment.offsetMs} | anchors=${segment.anchorCount} | '
        'confidence=${segment.confidence.toStringAsFixed(4)}',
      );
    }
    buffer.writeln();
  }
  return buffer.toString();
}
