import 'dart:io';

import 'package:asr_tools/models/asr_project.dart';
import 'package:asr_tools/models/media_file.dart';
import 'package:asr_tools/models/subtitle_file.dart';
import 'package:asr_tools/services/database_service.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:path/path.dart' as p;

import 'package:asr_tools/services/subtitle_prepare_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('low-value short phrase gets strong penalty', () {
    final normalized = SubtitlePrepareService.normalizeTextForMatching('嗯');
    final multiplier = SubtitlePrepareService.lowValuePhraseMultiplier(
      normalized,
    );

    expect(normalized, '嗯');
    expect(multiplier, 0.25);
  });

  test('low-value short sentence gets moderate penalty', () {
    final normalized = SubtitlePrepareService.normalizeTextForMatching('好 啊');
    final multiplier = SubtitlePrepareService.lowValuePhraseMultiplier(
      normalized,
    );

    expect(multiplier, 0.4);
  });

  test('normal sentence keeps default weight', () {
    final normalized = SubtitlePrepareService.normalizeTextForMatching(
      '我们今天从船尾进去',
    );
    final multiplier = SubtitlePrepareService.lowValuePhraseMultiplier(
      normalized,
    );

    expect(multiplier, 1.0);
  });

  test('prepareProject generates aggregate audio timeline from per-clip subtitles',
      () async {
    final tempDir = await Directory.systemTemp.createTemp(
      'subtitle-prepare-aggregate-test_',
    );
    final now = DateTime(2026, 5, 27, 12);
    try {
      await DatabaseService.init(
        overridePath: p.join(tempDir.path, 'aggregate-prepare.db'),
      );
      final project = AsrProject(
        id: 'project-1',
        name: 'aggregate prepare',
        createdAt: now,
        updatedAt: now,
      );
      await DatabaseService.insertProject(project);
      await DatabaseService.insertMediaFiles([
        MediaFile(
          id: 'audio-1',
          projectId: project.id,
          filePath: p.join(tempDir.path, 'A0001.wav'),
          type: MediaType.audio,
          durationMs: 5000,
          createdAt: now,
        ),
        MediaFile(
          id: 'audio-2',
          projectId: project.id,
          filePath: p.join(tempDir.path, 'A0002.wav'),
          type: MediaType.audio,
          durationMs: 5000,
          createdAt: now,
        ),
      ]);

      final subtitle1 = File(p.join(tempDir.path, 'A0001.srt'));
      final subtitle2 = File(p.join(tempDir.path, 'A0002.srt'));
      await subtitle1.writeAsString(
        '1\n00:00:01,000 --> 00:00:01,400\n第一句\n\n'
        '2\n00:00:03,000 --> 00:00:03,400\n第二句\n',
      );
      await subtitle2.writeAsString(
        '1\n00:00:00,500 --> 00:00:00,900\n第三句\n\n'
        '2\n00:00:02,000 --> 00:00:02,400\n第四句\n',
      );

      await DatabaseService.insertSubtitleFile(
        SubtitleFile(
          id: 'subtitle-1',
          projectId: project.id,
          filePath: subtitle1.path,
          mediaType: MediaType.audio,
          sourceType: SubtitleSourceType.perClip,
          createdAt: now,
        ),
      );
      await DatabaseService.insertSubtitleFile(
        SubtitleFile(
          id: 'subtitle-2',
          projectId: project.id,
          filePath: subtitle2.path,
          mediaType: MediaType.audio,
          sourceType: SubtitleSourceType.perClip,
          createdAt: now,
        ),
      );

      await SubtitlePrepareService.prepareProject(project.id);

      final aggregate = await DatabaseService.getPreferredAggregateAudioSubtitleFile(
        project.id,
      );
      final clips = await DatabaseService.getGlobalSubtitleClips(aggregate!.id);

      expect(aggregate.sourceType, SubtitleSourceType.generatedAggregate);
      expect(clips, hasLength(4));
      expect(clips.map((clip) => clip.startMs).toList(), [1000, 3000, 5500, 7000]);
    } finally {
      await DatabaseService.close();
      if (await tempDir.exists()) {
        await tempDir.delete(recursive: true);
      }
    }
  });
}
