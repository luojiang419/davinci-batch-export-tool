class TimelineAudioSegment {
  final int segmentIndex;
  final String audioFileId;
  final String audioFileName;
  final String audioFilePath;
  final int videoStartMs;
  final int videoEndMs;
  final int audioSourceInMs;
  final int audioSourceOutMs;
  final int offsetMs;
  final int anchorCount;
  final double confidence;
  final String? notes;

  const TimelineAudioSegment({
    required this.segmentIndex,
    required this.audioFileId,
    required this.audioFileName,
    required this.audioFilePath,
    required this.videoStartMs,
    required this.videoEndMs,
    required this.audioSourceInMs,
    required this.audioSourceOutMs,
    required this.offsetMs,
    this.anchorCount = 0,
    this.confidence = 0,
    this.notes,
  });

  int get videoDurationMs => videoEndMs - videoStartMs;
  int get audioDurationMs => audioSourceOutMs - audioSourceInMs;
}
