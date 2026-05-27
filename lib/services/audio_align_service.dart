import 'dart:io';
import 'dart:math' as math;

import 'package:path/path.dart' as p;

import '../models/subtitle_clip.dart';
import '../models/timeline_audio_segment.dart';
import '../models/timeline_data.dart';
import '../models/sync_result.dart';
import '../models/sync_audio_segment.dart';
import 'database_service.dart';
import 'ffmpeg_service.dart';

class AudioAlignService {
  AudioAlignService._();

  static Future<List<TimelineData>> buildTimeline(String projectId) async {
    final syncResults = await DatabaseService.getSyncResults(projectId);
    final timelines = <TimelineData>[];

    for (final syncResult in syncResults.where((item) => !item.isRejected)) {
      final timeline = await _buildSingleTimeline(syncResult);
      if (timeline != null) {
        timelines.add(timeline);
      }
    }

    return timelines;
  }

  static Future<TimelineData?> _buildSingleTimeline(
    SyncResult syncResult,
  ) async {
    final videoFile = await DatabaseService.getMediaFileById(
      syncResult.videoFileId,
    );
    if (videoFile == null) return null;
    final audioFile = syncResult.audioFileId == null
        ? null
        : await DatabaseService.getMediaFileById(syncResult.audioFileId!);
    var segmentRows = await DatabaseService.getSyncAudioSegments(syncResult.id);
    if (segmentRows.isEmpty &&
        syncResult.audioFileId != null &&
        syncResult.audioSourceInMs != null &&
        syncResult.audioSourceOutMs != null) {
      segmentRows = [
        SyncAudioSegment(
          id: syncResult.id,
          syncResultId: syncResult.id,
          segmentIndex: 0,
          audioFileId: syncResult.audioFileId!,
          videoStartMs: math.max(0, syncResult.timelineOffsetMs),
          videoEndMs: syncResult.videoDurationMs,
          audioSourceInMs: syncResult.audioSourceInMs!,
          audioSourceOutMs: syncResult.audioSourceOutMs!,
          offsetMs: syncResult.finalOffsetMs,
          anchorCount: syncResult.anchorCount,
          confidence: syncResult.confidence,
          notes: syncResult.notes,
          createdAt: syncResult.createdAt,
        ),
      ];
    }

    final videoSubtitles = await DatabaseService.getSubtitleClips(videoFile.id);
    final timelineSegments = await _buildTimelineSegments(segmentRows);
    final audioSubtitles = await _mapSegmentAudioSubtitles(
      timelineSegments,
      videoTimelineStartMs: syncResult.timelineStartMs,
    );

    final primarySegment = timelineSegments.isEmpty ? null : timelineSegments.first;
    final audioTrimStartMs = primarySegment?.audioSourceInMs ?? 0;
    final audioTrimEndMs = primarySegment?.audioSourceOutMs ?? 0;

    return TimelineData(
      syncResultId: syncResult.id,
      videoFileId: syncResult.videoFileId,
      audioFileId: syncResult.audioFileId,
      videoFileName: _fileName(videoFile.filePath),
      audioFileName: audioFile == null
          ? '未匹配音频'
          : _fileName(audioFile.filePath),
      videoFilePath: videoFile.filePath,
      audioFilePath: primarySegment?.audioFilePath ?? audioFile?.filePath ?? '',
      videoHasEmbeddedAudio: videoFile.hasEmbeddedAudio,
      videoStartMs: 0,
      videoEndMs: syncResult.videoDurationMs,
      timelineStartMs: syncResult.timelineStartMs,
      timelineEndMs: syncResult.timelineEndMs,
      audioOriginalDurationMs:
          primarySegment == null ? (audioFile?.durationMs ?? 0) : primarySegment.audioDurationMs,
      audioTrimStartMs: audioTrimStartMs,
      audioTrimEndMs: audioTrimEndMs,
      offsetMs: syncResult.timelineOffsetMs,
      confidence: syncResult.confidence,
      status: syncResult.status.label,
      method: syncResult.method.name,
      markerText: _buildMarkerText(syncResult, audioFile?.filePath ?? ''),
      anchorCount: syncResult.anchorCount,
      sourceClamped: syncResult.sourceClamped,
      audioTooShort: syncResult.audioTooShort,
      coarseOffsetMs: syncResult.coarseOffsetMs,
      finalOffsetMs: syncResult.finalOffsetMs,
      offsetMadMs: syncResult.offsetMadMs,
      alignmentCoverage: syncResult.alignmentCoverage,
      switchCount: syncResult.switchCount,
      sourceClampedReason: syncResult.sourceClampedReason,
      reviewStatus: syncResult.reviewStatus,
      reviewedAtMs: syncResult.reviewedAtMs,
      reviewNote: syncResult.reviewNote,
      segments: timelineSegments,
      videoSubtitles: videoSubtitles,
      audioSubtitles: audioSubtitles,
    );
  }

  static Future<List<TimelineAudioSegment>> _buildTimelineSegments(
    List<SyncAudioSegment> segments,
  ) async {
    final rows = <TimelineAudioSegment>[];
    for (final segment in segments) {
      final audioFile = await DatabaseService.getMediaFileById(segment.audioFileId);
      if (audioFile == null) continue;
      rows.add(
        TimelineAudioSegment(
          segmentIndex: segment.segmentIndex,
          audioFileId: segment.audioFileId,
          audioFileName: _fileName(audioFile.filePath),
          audioFilePath: audioFile.filePath,
          videoStartMs: segment.videoStartMs,
          videoEndMs: segment.videoEndMs,
          audioSourceInMs: segment.audioSourceInMs,
          audioSourceOutMs: segment.audioSourceOutMs,
          offsetMs: segment.offsetMs,
          anchorCount: segment.anchorCount,
          confidence: segment.confidence,
          notes: segment.notes,
        ),
      );
    }
    rows.sort((left, right) => left.segmentIndex.compareTo(right.segmentIndex));
    return rows;
  }

  static List<SubtitleClip> _mapAudioSubtitlesToTimeline(
    List<SubtitleClip> clips, {
    required int videoTimelineStartMs,
    required int audioSourceInMs,
  }) {
    return clips
        .where((clip) {
          final localEnd = clip.localEndMs ?? clip.endMs;
          return localEnd >= audioSourceInMs;
        })
        .map((clip) {
          final localStart = clip.localStartMs ?? clip.startMs;
          final localEnd = clip.localEndMs ?? clip.endMs;
          final mappedStart =
              videoTimelineStartMs + (localStart - audioSourceInMs);
          final mappedEnd = videoTimelineStartMs + (localEnd - audioSourceInMs);
          return SubtitleClip(
            id: clip.id,
            subtitleFileId: clip.subtitleFileId,
            mediaFileId: clip.mediaFileId,
            sourceKind: clip.sourceKind,
            startMs: mappedStart,
            endMs: mappedEnd,
            globalStartMs: clip.globalStartMs,
            globalEndMs: clip.globalEndMs,
            localStartMs: mappedStart,
            localEndMs: mappedEnd,
            text: clip.text,
            normalizedText: clip.normalizedText,
            sortOrder: clip.sortOrder,
          );
        })
        .where((clip) => clip.endMs > clip.startMs)
        .toList();
  }

  static Future<List<SubtitleClip>> _mapSegmentAudioSubtitles(
    List<TimelineAudioSegment> segments, {
    required int videoTimelineStartMs,
  }) async {
    final mapped = <SubtitleClip>[];
    for (final segment in segments) {
      final clips = await DatabaseService.getSubtitleClips(segment.audioFileId);
      final segmentMapped = _mapAudioSubtitlesToTimeline(
        clips.where((clip) {
          final localStart = clip.localStartMs ?? clip.startMs;
          final localEnd = clip.localEndMs ?? clip.endMs;
          return localEnd > segment.audioSourceInMs &&
              localStart < segment.audioSourceOutMs;
        }).toList(),
        videoTimelineStartMs: videoTimelineStartMs + segment.videoStartMs,
        audioSourceInMs: segment.audioSourceInMs,
      ).map((clip) {
        return SubtitleClip(
          id: '${segment.segmentIndex}_${clip.id}',
          subtitleFileId: clip.subtitleFileId,
          mediaFileId: clip.mediaFileId,
          sourceKind: clip.sourceKind,
          startMs: clip.startMs,
          endMs: clip.endMs,
          globalStartMs: clip.globalStartMs,
          globalEndMs: clip.globalEndMs,
          localStartMs: clip.localStartMs,
          localEndMs: clip.localEndMs,
          text: clip.text,
          normalizedText: clip.normalizedText,
          sortOrder: clip.sortOrder,
        );
      });
      mapped.addAll(segmentMapped);
    }
    mapped.sort((left, right) => left.startMs.compareTo(right.startMs));
    return mapped;
  }

  static Future<List<String>> batchTrimAudio(
    List<TimelineData> timelineList,
    String outputDir, {
    required void Function(int current, int total, String fileName) onProgress,
  }) async {
    final dir = Directory(outputDir);
    if (!await dir.exists()) {
      await dir.create(recursive: true);
    }

    final results = <String>[];
    final total = timelineList.length;

    for (var i = 0; i < timelineList.length; i++) {
      final timeline = timelineList[i];
      if (timeline.audioFilePath.isEmpty || timeline.audioDurationMs <= 0) {
        results.add('');
        continue;
      }
      final outputFileName =
          '${_removeExtension(timeline.videoFileName)}_aligned.wav';
      final outputPath = p.join(outputDir, outputFileName);

      onProgress(i + 1, total, timeline.audioFileName);

      try {
        await FfmpegService.trimAndConvert(
          inputPath: timeline.audioFilePath,
          outputPath: outputPath,
          startMs: timeline.audioTrimStartMs,
          endMs: timeline.audioTrimEndMs,
        );
        results.add(outputPath);
      } catch (_) {
        results.add('');
      }
    }

    return results;
  }

  static String _buildMarkerText(SyncResult syncResult, String audioPath) {
    final fileName = audioPath.isEmpty ? '无音频' : _fileName(audioPath);
    final sourceIn = syncResult.audioSourceInMs == null
        ? '--'
        : _formatTime(syncResult.audioSourceInMs!);
    final sourceOut = syncResult.audioSourceOutMs == null
        ? '--'
        : _formatTime(syncResult.audioSourceOutMs!);
    return '${syncResult.status.label} ${(syncResult.confidence * 100).toStringAsFixed(0)}% | '
        '$fileName | $sourceIn - $sourceOut | anchors=${syncResult.anchorCount} | segments=${math.max(1, syncResult.switchCount + 1)}';
  }

  static String _fileName(String path) => p.basename(path);

  static String _removeExtension(String fileName) {
    final dotIndex = fileName.lastIndexOf('.');
    if (dotIndex > 0) return fileName.substring(0, dotIndex);
    return fileName;
  }

  static String _formatTime(int ms) {
    final h = (ms ~/ 3600000).toString().padLeft(2, '0');
    final m = ((ms % 3600000) ~/ 60000).toString().padLeft(2, '0');
    final s = ((ms % 60000) ~/ 1000).toString().padLeft(2, '0');
    return '$h:$m:$s';
  }
}
