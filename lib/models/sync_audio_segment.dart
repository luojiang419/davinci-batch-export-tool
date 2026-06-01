class SyncAudioSegment {
  final String id;
  final String syncResultId;
  final int segmentIndex;
  final String audioFileId;
  final int videoStartMs;
  final int videoEndMs;
  final int audioSourceInMs;
  final int audioSourceOutMs;
  final int offsetMs;
  final int anchorCount;
  final double confidence;
  final String? notes;
  final DateTime createdAt;

  const SyncAudioSegment({
    required this.id,
    required this.syncResultId,
    required this.segmentIndex,
    required this.audioFileId,
    required this.videoStartMs,
    required this.videoEndMs,
    required this.audioSourceInMs,
    required this.audioSourceOutMs,
    required this.offsetMs,
    this.anchorCount = 0,
    this.confidence = 0,
    this.notes,
    required this.createdAt,
  });

  int get videoDurationMs => videoEndMs - videoStartMs;
  int get audioDurationMs => audioSourceOutMs - audioSourceInMs;

  factory SyncAudioSegment.fromMap(Map<String, dynamic> map) {
    return SyncAudioSegment(
      id: map['id'] as String,
      syncResultId: map['sync_result_id'] as String,
      segmentIndex: map['segment_index'] as int? ?? 0,
      audioFileId: map['audio_file_id'] as String,
      videoStartMs: map['video_start_ms'] as int? ?? 0,
      videoEndMs: map['video_end_ms'] as int? ?? 0,
      audioSourceInMs: map['audio_source_in_ms'] as int? ?? 0,
      audioSourceOutMs: map['audio_source_out_ms'] as int? ?? 0,
      offsetMs: map['offset_ms'] as int? ?? 0,
      anchorCount: map['anchor_count'] as int? ?? 0,
      confidence: (map['confidence'] as num?)?.toDouble() ?? 0.0,
      notes: map['notes'] as String?,
      createdAt: DateTime.fromMillisecondsSinceEpoch(map['created_at'] as int),
    );
  }

  Map<String, dynamic> toMap() => {
    'id': id,
    'sync_result_id': syncResultId,
    'segment_index': segmentIndex,
    'audio_file_id': audioFileId,
    'video_start_ms': videoStartMs,
    'video_end_ms': videoEndMs,
    'audio_source_in_ms': audioSourceInMs,
    'audio_source_out_ms': audioSourceOutMs,
    'offset_ms': offsetMs,
    'anchor_count': anchorCount,
    'confidence': confidence,
    'notes': notes,
    'created_at': createdAt.millisecondsSinceEpoch,
  };
}
