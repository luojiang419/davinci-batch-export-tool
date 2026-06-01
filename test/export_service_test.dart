import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:path/path.dart' as p;
import 'package:xml/xml.dart';

import 'package:asr_tools/models/timeline_audio_segment.dart';
import 'package:asr_tools/models/timeline_data.dart';
import 'package:asr_tools/services/export_service.dart';

void main() {
  late Directory tempDir;

  setUp(() async {
    tempDir = await Directory.systemTemp.createTemp('export-service-test-');
  });

  tearDown(() async {
    if (await tempDir.exists()) {
      await tempDir.delete(recursive: true);
    }
  });

  test(
    'sanitize export base name trims and replaces Windows invalid chars',
    () {
      final sanitized = ExportService.sanitizeExportBaseName(
        '  工程:测试?版本*1  ',
        fallbackName: '备用名称',
      );

      expect(sanitized, '工程_测试_版本_1');
    },
  );

  test('sanitize export base name falls back when input becomes empty', () {
    final sanitized = ExportService.sanitizeExportBaseName(
      '   ',
      fallbackName: '默认工程名',
    );

    expect(sanitized, '默认工程名');
  });

  test(
    'sanitize export base name falls back to ASR Timeline as last resort',
    () {
      final sanitized = ExportService.sanitizeExportBaseName(
        '///',
        fallbackName: ':::',
      );

      expect(sanitized, 'ASR Timeline');
    },
  );

  test(
    'xmeml keeps embedded audio and external audio on separate tracks',
    () async {
      final outputPath = p.join(tempDir.path, 'timeline.xml');
      final timeline = _buildTimelineData(
        videoHasEmbeddedAudio: true,
        audioFileId: 'audio-1',
        audioFileName: 'A0001.wav',
        audioFilePath: r'G:\audio\A0001.wav',
        audioOriginalDurationMs: 6000,
        audioTrimStartMs: 300,
        audioTrimEndMs: 4300,
      );

      await ExportService.exportXmeml([timeline], outputPath);
      final document = XmlDocument.parse(await File(outputPath).readAsString());
      final sequence = document.findAllElements('sequence').first;
      final timelineAudio = sequence
          .findElements('media')
          .first
          .findElements('audio')
          .first;
      final videoClip = sequence
          .findAllElements('video')
          .first
          .findElements('track')
          .first
          .findElements('clipitem')
          .first;
      final videoFileId = videoClip
          .findElements('file')
          .first
          .getAttribute('id');
      final audioTracks = timelineAudio.findElements('track').toList();

      expect(audioTracks.length, 2);

      final embeddedClip = audioTracks[0].findElements('clipitem').first;
      expect(
        embeddedClip.findElements('file').first.getAttribute('id'),
        videoFileId,
      );
      expect(
        embeddedClip
            .findElements('sourcetrack')
            .first
            .findElements('mediatype')
            .first
            .innerText,
        'audio',
      );

      final externalClip = audioTracks[1].findElements('clipitem').first;
      expect(
        externalClip
            .findElements('file')
            .first
            .findElements('pathurl')
            .first
            .innerText,
        contains('A0001.wav'),
      );
      expect(
        externalClip
            .findElements('file')
            .first
            .findElements('timecode')
            .first
            .findElements('string')
            .first
            .innerText,
        '00:00:00:00',
      );
    },
  );

  test(
    'xmeml skips embedded audio track when video has no embedded audio',
    () async {
      final outputPath = p.join(tempDir.path, 'timeline-no-embedded.xml');
      final timeline = _buildTimelineData(
        videoHasEmbeddedAudio: false,
        audioFileId: 'audio-1',
        audioFileName: 'A0001.wav',
        audioFilePath: r'G:\audio\A0001.wav',
        audioOriginalDurationMs: 6000,
        audioTrimStartMs: 300,
        audioTrimEndMs: 4300,
      );

      await ExportService.exportXmeml([timeline], outputPath);
      final document = XmlDocument.parse(await File(outputPath).readAsString());
      final sequence = document.findAllElements('sequence').first;
      final audioTracks = sequence
          .findElements('media')
          .first
          .findElements('audio')
          .first
          .findElements('track')
          .toList();

      expect(audioTracks.length, 1);
      expect(
        audioTracks.first
            .findElements('clipitem')
            .first
            .findElements('name')
            .first
            .innerText,
        'A0001.wav',
      );
    },
  );

  test(
    'xmeml skips external audio track when match has no external audio',
    () async {
      final outputPath = p.join(tempDir.path, 'timeline-no-external.xml');
      final timeline = _buildTimelineData(videoHasEmbeddedAudio: true);

      await ExportService.exportXmeml([timeline], outputPath);
      final document = XmlDocument.parse(await File(outputPath).readAsString());
      final sequence = document.findAllElements('sequence').first;
      final timelineAudio = sequence
          .findElements('media')
          .first
          .findElements('audio')
          .first;
      final videoClip = sequence
          .findAllElements('video')
          .first
          .findElements('track')
          .first
          .findElements('clipitem')
          .first;
      final videoFileId = videoClip
          .findElements('file')
          .first
          .getAttribute('id');
      final audioTracks = timelineAudio.findElements('track').toList();

      expect(audioTracks.length, 1);
      expect(
        audioTracks.first
            .findElements('clipitem')
            .first
            .findElements('file')
            .first
            .getAttribute('id'),
        videoFileId,
      );
    },
  );

  test(
    'fcpxml exports embedded and external audio as separate sequence audio lanes',
    () async {
      final outputPath = p.join(tempDir.path, 'timeline.fcpxml');
      final timeline = _buildTimelineData(
        videoHasEmbeddedAudio: true,
        audioFileId: 'audio-1',
        audioFileName: 'A0001.wav',
        audioFilePath: r'G:\audio\A0001.wav',
        audioOriginalDurationMs: 6000,
        audioTrimStartMs: 300,
        audioTrimEndMs: 4300,
      );

      await ExportService.exportFcpxml([timeline], outputPath);
      final document = XmlDocument.parse(await File(outputPath).readAsString());
      final sequence = document.findAllElements('sequence').first;
      final audioElements = sequence.findElements('audio').toList();

      expect(audioElements.length, 2);
      expect(audioElements[0].getAttribute('ref'), 'a_video-1');
      expect(audioElements[0].getAttribute('lane'), '-1');
      expect(audioElements[1].getAttribute('ref'), 'a_audio-1');
      expect(audioElements[1].getAttribute('lane'), '-2');
    },
  );

  test(
    'fcpxml skips missing embedded audio lane and keeps external lane',
    () async {
      final outputPath = p.join(tempDir.path, 'timeline-external-only.fcpxml');
      final timeline = _buildTimelineData(
        videoHasEmbeddedAudio: false,
        audioFileId: 'audio-1',
        audioFileName: 'A0001.wav',
        audioFilePath: r'G:\audio\A0001.wav',
        audioOriginalDurationMs: 6000,
        audioTrimStartMs: 300,
        audioTrimEndMs: 4300,
      );

      await ExportService.exportFcpxml([timeline], outputPath);
      final document = XmlDocument.parse(await File(outputPath).readAsString());
      final audioElements = document
          .findAllElements('sequence')
          .first
          .findElements('audio')
          .toList();

      expect(audioElements.length, 1);
      expect(audioElements.first.getAttribute('ref'), 'a_audio-1');
      expect(audioElements.first.getAttribute('lane'), '-2');
    },
  );

  test(
    'xmeml exports multiple external audio clipitems for segmented audio',
    () async {
      final outputPath = p.join(tempDir.path, 'timeline-multi.xml');
      final timeline = _buildTimelineData(
        videoHasEmbeddedAudio: false,
        segments: const [
          TimelineAudioSegment(
            segmentIndex: 0,
            audioFileId: 'audio-1',
            audioFileName: 'A0001.wav',
            audioFilePath: r'G:\audio\A0001.wav',
            videoStartMs: 0,
            videoEndMs: 2000,
            audioSourceInMs: 1000,
            audioSourceOutMs: 3000,
            offsetMs: 1000,
          ),
          TimelineAudioSegment(
            segmentIndex: 1,
            audioFileId: 'audio-2',
            audioFileName: 'A0002.wav',
            audioFilePath: r'G:\audio\A0002.wav',
            videoStartMs: 2000,
            videoEndMs: 4000,
            audioSourceInMs: 500,
            audioSourceOutMs: 2500,
            offsetMs: 1500,
          ),
        ],
      );

      await ExportService.exportXmeml([timeline], outputPath);
      final document = XmlDocument.parse(await File(outputPath).readAsString());
      final tracks = document
          .findAllElements('sequence')
          .first
          .findElements('media')
          .first
          .findElements('audio')
          .first
          .findElements('track')
          .toList();
      final externalTrack = tracks.last;

      expect(externalTrack.findElements('clipitem').length, 2);
    },
  );

  test(
    'xmeml reuses shared audio file definition with full source duration',
    () async {
      final outputPath = p.join(tempDir.path, 'timeline-shared-audio.xml');
      final sharedSegments = const [
        TimelineAudioSegment(
          segmentIndex: 0,
          audioFileId: 'audio-1',
          audioFileName: 'A0001.wav',
          audioFilePath: r'G:\audio\A0001.wav',
          audioFileDurationMs: 120000,
          videoStartMs: 0,
          videoEndMs: 2000,
          audioSourceInMs: 40000,
          audioSourceOutMs: 42000,
          offsetMs: 40000,
        ),
      ];
      final first = _buildTimelineData(
        videoHasEmbeddedAudio: false,
        segments: sharedSegments,
      );
      final second = TimelineData(
        syncResultId: 'sync-2',
        videoFileId: 'video-2',
        videoFileName: 'C0002.mp4',
        videoFilePath: r'G:\video\C0002.mp4',
        videoEndMs: 3000,
        timelineEndMs: 3000,
        confidence: 0.9,
        status: '已通过',
        method: 'subtitleOnly',
        segments: const [
          TimelineAudioSegment(
            segmentIndex: 0,
            audioFileId: 'audio-1',
            audioFileName: 'A0001.wav',
            audioFilePath: r'G:\audio\A0001.wav',
            audioFileDurationMs: 120000,
            videoStartMs: 0,
            videoEndMs: 3000,
            audioSourceInMs: 80000,
            audioSourceOutMs: 83000,
            offsetMs: 80000,
          ),
        ],
      );

      await ExportService.exportXmeml([first, second], outputPath);
      final document = XmlDocument.parse(await File(outputPath).readAsString());
      final files = document
          .findAllElements('clipitem')
          .where((clip) => clip.findElements('sourcetrack').isNotEmpty)
          .expand((clip) => clip.findElements('file'))
          .where((file) {
            final names = file.findElements('name');
            final name = names.isEmpty ? null : names.first.innerText;
            final refId = file.getAttribute('id') ?? '';
            return name == 'A0001.wav' || refId.contains('A0001_wav');
          })
          .toList();

      final fullDefinitions = files
          .where((file) => file.findElements('duration').isNotEmpty)
          .toList();
      expect(fullDefinitions, hasLength(1));
      expect(
        fullDefinitions.first.findElements('duration').first.innerText,
        '2880',
      );
      final secondRef = files.last;
      expect(secondRef.findElements('duration'), isEmpty);
    },
  );

  test('xmeml external audio file duration always covers clip out', () async {
    final outputPath = p.join(tempDir.path, 'timeline-source-duration.xml');
    final timeline = _buildTimelineData(
      videoHasEmbeddedAudio: false,
      segments: const [
        TimelineAudioSegment(
          segmentIndex: 0,
          audioFileId: 'audio-1',
          audioFileName: 'A0001.wav',
          audioFilePath: r'G:\audio\A0001.wav',
          audioFileDurationMs: 1200000,
          videoStartMs: 0,
          videoEndMs: 4000,
          audioSourceInMs: 681190,
          audioSourceOutMs: 936529,
          offsetMs: 2410919,
        ),
      ],
    );

    await ExportService.exportXmeml([timeline], outputPath);
    final document = XmlDocument.parse(await File(outputPath).readAsString());
    final clip = document
        .findAllElements('clipitem')
        .firstWhere((item) => item.findElements('sourcetrack').isNotEmpty);
    final file = clip.findElements('file').first;
    final duration = int.parse(file.findElements('duration').first.innerText);
    final out = int.parse(clip.findElements('out').first.innerText);

    expect(duration, greaterThanOrEqualTo(out));
  });

  test(
    'xmeml writes Premiere ticks and master clip ids for external audio',
    () async {
      final outputPath = p.join(
        tempDir.path,
        'timeline-premiere-compatible.xml',
      );
      final timeline = _buildTimelineData(
        videoHasEmbeddedAudio: false,
        segments: const [
          TimelineAudioSegment(
            segmentIndex: 0,
            audioFileId: 'audio-1',
            audioFileName: 'A0001.wav',
            audioFilePath: r'G:\audio\A0001.wav',
            audioFileDurationMs: 1200000,
            videoStartMs: 0,
            videoEndMs: 4000,
            audioSourceInMs: 681190,
            audioSourceOutMs: 936529,
            offsetMs: 2410919,
          ),
        ],
      );

      await ExportService.exportXmeml([timeline], outputPath);
      final document = XmlDocument.parse(await File(outputPath).readAsString());
      final clip = document
          .findAllElements('clipitem')
          .firstWhere((item) => item.findElements('sourcetrack').isNotEmpty);

      expect(clip.findElements('masterclipid').single.innerText, isNotEmpty);

      final inFrames = int.parse(clip.findElements('in').single.innerText);
      final outFrames = int.parse(clip.findElements('out').single.innerText);
      final ticksIn = clip.findElements('pproTicksIn').single.innerText;
      final ticksOut = clip.findElements('pproTicksOut').single.innerText;

      expect(ticksIn, _premiereTicksForFrames(inFrames));
      expect(ticksOut, _premiereTicksForFrames(outFrames));
    },
  );

  test(
    'fcpxml exports multiple external audio elements for segmented audio',
    () async {
      final outputPath = p.join(tempDir.path, 'timeline-multi.fcpxml');
      final timeline = _buildTimelineData(
        videoHasEmbeddedAudio: false,
        segments: const [
          TimelineAudioSegment(
            segmentIndex: 0,
            audioFileId: 'audio-1',
            audioFileName: 'A0001.wav',
            audioFilePath: r'G:\audio\A0001.wav',
            videoStartMs: 0,
            videoEndMs: 2000,
            audioSourceInMs: 1000,
            audioSourceOutMs: 3000,
            offsetMs: 1000,
          ),
          TimelineAudioSegment(
            segmentIndex: 1,
            audioFileId: 'audio-2',
            audioFileName: 'A0002.wav',
            audioFilePath: r'G:\audio\A0002.wav',
            videoStartMs: 2000,
            videoEndMs: 4000,
            audioSourceInMs: 500,
            audioSourceOutMs: 2500,
            offsetMs: 1500,
          ),
        ],
      );

      await ExportService.exportFcpxml([timeline], outputPath);
      final document = XmlDocument.parse(await File(outputPath).readAsString());
      final audioElements = document
          .findAllElements('sequence')
          .first
          .findElements('audio')
          .toList();

      expect(audioElements.length, 2);
      expect(
        audioElements.map((item) => item.getAttribute('ref')),
        containsAll(['a_audio-1', 'a_audio-2']),
      );
    },
  );
}

TimelineData _buildTimelineData({
  required bool videoHasEmbeddedAudio,
  String? audioFileId,
  String audioFileName = '',
  String audioFilePath = '',
  int audioOriginalDurationMs = 0,
  int audioTrimStartMs = 0,
  int audioTrimEndMs = 0,
  List<TimelineAudioSegment> segments = const [],
  String videoFileId = 'video-1',
  String videoFileName = 'C0001.mp4',
  String videoFilePath = r'G:\video\C0001.mp4',
  int videoEndMs = 4000,
  int timelineEndMs = 4000,
}) {
  return TimelineData(
    syncResultId: 'sync-1',
    videoFileId: videoFileId,
    audioFileId: audioFileId,
    videoFileName: videoFileName,
    audioFileName: audioFileName,
    videoFilePath: videoFilePath,
    audioFilePath: audioFilePath,
    videoHasEmbeddedAudio: videoHasEmbeddedAudio,
    videoEndMs: videoEndMs,
    timelineEndMs: timelineEndMs,
    audioOriginalDurationMs: audioOriginalDurationMs,
    audioTrimStartMs: audioTrimStartMs,
    audioTrimEndMs: audioTrimEndMs,
    offsetMs: 0, // timeline offset, 0 for non-clamped case
    confidence: 0.92,
    status: '已通过',
    method: 'subtitleOnly',
    segments: segments,
  );
}

String _premiereTicksForFrames(int frames) {
  const ticksPerSecond = 254016000000;
  const fps = 24;
  if (frames <= 0) return '0';
  return ((BigInt.from(frames) * BigInt.from(ticksPerSecond)) ~/
          BigInt.from(fps))
      .toString();
}
