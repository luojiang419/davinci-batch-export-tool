import 'dart:io';

import 'package:asr_tools/models/asr_project.dart';
import 'package:asr_tools/models/media_file.dart';
import 'package:asr_tools/models/subtitle_clip.dart';
import 'package:asr_tools/models/subtitle_file.dart';
import 'package:asr_tools/services/audio_align_service.dart';
import 'package:asr_tools/services/database_service.dart';
import 'package:asr_tools/services/subtitle_match_service.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:path/path.dart' as p;

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late Directory tempDir;

  setUp(() async {
    tempDir = await Directory.systemTemp.createTemp('multi-segment-match-test_');
    await DatabaseService.init(
      overridePath: p.join(tempDir.path, 'multi-segment-match.db'),
    );
  });

  tearDown(() async {
    await DatabaseService.close();
    if (await tempDir.exists()) {
      await tempDir.delete(recursive: true);
    }
  });

  test('matchProject keeps positive headroom without false sourceClamped', () async {
    final project = await _seedSingleAudioProject(
      projectId: 'project-single',
      videoDurationMs: 8000,
      audioDurationsMs: const [12000],
      videoCueStarts: const [2000, 4000, 6000],
      aggregateCueStarts: const [3000, 5000, 7000],
    );

    final results = await SubtitleMatchService.matchProject(projectId: project.id);

    expect(results, hasLength(1));
    expect(results.first.sourceClamped, isFalse);
    expect(results.first.audioFileId, 'audio-1');
    final segments = await DatabaseService.getSyncAudioSegments(results.first.id);
    expect(segments, hasLength(1));
    expect(segments.first.audioSourceInMs, 1000);
    expect(segments.first.videoStartMs, 0);
  });

  test('matchProject creates multiple audio segments and reaches video end', () async {
    final project = await _seedMultiAudioProject();

    final results = await SubtitleMatchService.matchProject(projectId: project.id);

    expect(results, hasLength(1));
    final result = results.first;
    final segments = await DatabaseService.getSyncAudioSegments(result.id);

    expect(segments.length, greaterThanOrEqualTo(2));
    expect(segments.first.audioFileId, 'audio-1');
    expect(segments.last.audioFileId, 'audio-2');
    expect(segments.last.videoEndMs, 12000);
    expect(result.switchCount, greaterThanOrEqualTo(1));

    final timeline = await AudioAlignService.buildTimeline(project.id);
    expect(timeline, hasLength(1));
    expect(timeline.first.segments.length, greaterThanOrEqualTo(2));
    expect(timeline.first.audioSubtitles.length, greaterThanOrEqualTo(4));
  });
}

Future<AsrProject> _seedSingleAudioProject({
  required String projectId,
  required int videoDurationMs,
  required List<int> audioDurationsMs,
  required List<int> videoCueStarts,
  required List<int> aggregateCueStarts,
}) async {
  final now = DateTime(2026, 5, 27, 13);
  final project = AsrProject(
    id: projectId,
    name: projectId,
    createdAt: now,
    updatedAt: now,
  );
  await DatabaseService.insertProject(project);
  await DatabaseService.insertMediaFiles([
    MediaFile(
      id: 'video-1',
      projectId: project.id,
      filePath: r'G:\video\C0001.mp4',
      type: MediaType.video,
      durationMs: videoDurationMs,
      layoutStartMs: 0,
      layoutEndMs: videoDurationMs,
      createdAt: now,
    ),
    MediaFile(
      id: 'audio-1',
      projectId: project.id,
      filePath: r'G:\audio\A0001.wav',
      type: MediaType.audio,
      durationMs: audioDurationsMs.first,
      layoutStartMs: 0,
      layoutEndMs: audioDurationsMs.first,
      createdAt: now,
    ),
  ]);
  await DatabaseService.insertSubtitleFile(
    SubtitleFile(
      id: 'audio-aggregate',
      projectId: project.id,
      filePath: r'G:\subtitle\all_audio.srt',
      mediaType: MediaType.audio,
      sourceType: SubtitleSourceType.aggregate,
      createdAt: now,
    ),
  );
  await DatabaseService.insertSubtitleClips([
    for (var index = 0; index < videoCueStarts.length; index++)
      SubtitleClip(
        id: 'video-$index',
        mediaFileId: 'video-1',
        sourceKind: 'local',
        startMs: videoCueStarts[index],
        endMs: videoCueStarts[index] + 400,
        localStartMs: videoCueStarts[index],
        localEndMs: videoCueStarts[index] + 400,
        text: '句子${index + 1}',
        normalizedText: '句子${index + 1}',
        sortOrder: index,
      ),
    for (var index = 0; index < aggregateCueStarts.length; index++)
      SubtitleClip(
        id: 'agg-$index',
        subtitleFileId: 'audio-aggregate',
        sourceKind: 'aggregate',
        startMs: aggregateCueStarts[index],
        endMs: aggregateCueStarts[index] + 400,
        globalStartMs: aggregateCueStarts[index],
        globalEndMs: aggregateCueStarts[index] + 400,
        text: '句子${index + 1}',
        normalizedText: '句子${index + 1}',
        sortOrder: index,
      ),
    for (var index = 0; index < aggregateCueStarts.length; index++)
      SubtitleClip(
        id: 'local-$index',
        mediaFileId: 'audio-1',
        sourceKind: 'derived',
        startMs: aggregateCueStarts[index],
        endMs: aggregateCueStarts[index] + 400,
        localStartMs: aggregateCueStarts[index],
        localEndMs: aggregateCueStarts[index] + 400,
        globalStartMs: aggregateCueStarts[index],
        globalEndMs: aggregateCueStarts[index] + 400,
        text: '句子${index + 1}',
        normalizedText: '句子${index + 1}',
        sortOrder: index,
      ),
  ]);
  return project;
}

Future<AsrProject> _seedMultiAudioProject() async {
  final now = DateTime(2026, 5, 27, 14);
  final project = AsrProject(
    id: 'project-multi',
    name: 'project-multi',
    createdAt: now,
    updatedAt: now,
  );
  await DatabaseService.insertProject(project);
  await DatabaseService.insertMediaFiles([
    MediaFile(
      id: 'video-1',
      projectId: project.id,
      filePath: r'G:\video\C0002.mp4',
      type: MediaType.video,
      durationMs: 12000,
      layoutStartMs: 0,
      layoutEndMs: 12000,
      createdAt: now,
    ),
    MediaFile(
      id: 'audio-1',
      projectId: project.id,
      filePath: r'G:\audio\A1001.wav',
      type: MediaType.audio,
      durationMs: 7000,
      layoutStartMs: 0,
      layoutEndMs: 7000,
      createdAt: now,
    ),
    MediaFile(
      id: 'audio-2',
      projectId: project.id,
      filePath: r'G:\audio\A1002.wav',
      type: MediaType.audio,
      durationMs: 7000,
      layoutStartMs: 7000,
      layoutEndMs: 14000,
      createdAt: now,
    ),
  ]);
  await DatabaseService.insertSubtitleFile(
    SubtitleFile(
      id: 'audio-aggregate',
      projectId: project.id,
      filePath: r'G:\subtitle\all_audio.srt',
      mediaType: MediaType.audio,
      sourceType: SubtitleSourceType.aggregate,
      createdAt: now,
    ),
  );
  final videoCueStarts = [1000, 4000, 8000, 11000];
  final aggregateCueStarts = [2000, 5000, 10000, 13000];
  await DatabaseService.insertSubtitleClips([
    for (var index = 0; index < videoCueStarts.length; index++)
      SubtitleClip(
        id: 'video-$index',
        mediaFileId: 'video-1',
        sourceKind: 'local',
        startMs: videoCueStarts[index],
        endMs: videoCueStarts[index] + 400,
        localStartMs: videoCueStarts[index],
        localEndMs: videoCueStarts[index] + 400,
        text: '片段${index + 1}',
        normalizedText: '片段${index + 1}',
        sortOrder: index,
      ),
    for (var index = 0; index < aggregateCueStarts.length; index++)
      SubtitleClip(
        id: 'agg-$index',
        subtitleFileId: 'audio-aggregate',
        sourceKind: 'aggregate',
        startMs: aggregateCueStarts[index],
        endMs: aggregateCueStarts[index] + 400,
        globalStartMs: aggregateCueStarts[index],
        globalEndMs: aggregateCueStarts[index] + 400,
        text: '片段${index + 1}',
        normalizedText: '片段${index + 1}',
        sortOrder: index,
      ),
    for (var index = 0; index < 2; index++)
      SubtitleClip(
        id: 'audio1-$index',
        mediaFileId: 'audio-1',
        sourceKind: 'derived',
        startMs: [2000, 5000][index],
        endMs: [2400, 5400][index],
        localStartMs: [2000, 5000][index],
        localEndMs: [2400, 5400][index],
        globalStartMs: [2000, 5000][index],
        globalEndMs: [2400, 5400][index],
        text: '片段${index + 1}',
        normalizedText: '片段${index + 1}',
        sortOrder: index,
      ),
    for (var index = 0; index < 2; index++)
      SubtitleClip(
        id: 'audio2-$index',
        mediaFileId: 'audio-2',
        sourceKind: 'derived',
        startMs: [3000, 6000][index],
        endMs: [3400, 6400][index],
        localStartMs: [3000, 6000][index],
        localEndMs: [3400, 6400][index],
        globalStartMs: [10000, 13000][index],
        globalEndMs: [10400, 13400][index],
        text: '片段${index + 3}',
        normalizedText: '片段${index + 3}',
        sortOrder: index,
      ),
  ]);
  return project;
}
