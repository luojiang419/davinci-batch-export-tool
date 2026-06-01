import 'dart:io';

import 'package:asr_tools/core/constants.dart';
import 'package:asr_tools/services/database_service.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:path/path.dart' as p;
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

void main() {
  late Directory tempDir;

  setUp(() async {
    tempDir = await Directory.systemTemp.createTemp(
      'database-service-init-test_',
    );
  });

  tearDown(() async {
    await DatabaseService.close();
    if (await tempDir.exists()) {
      await tempDir.delete(recursive: true);
    }
  });

  test('init tolerates prebuilt schema with zero user_version', () async {
    final dbPath = p.join(tempDir.path, AppConstants.dbName);

    await DatabaseService.init(overridePath: dbPath);
    await DatabaseService.close();

    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi;
    final rawDb = await databaseFactory.openDatabase(dbPath);
    await rawDb.execute('PRAGMA user_version = 0');
    await rawDb.close();

    await DatabaseService.init(overridePath: dbPath);

    expect(await DatabaseService.getAllProjects(), isEmpty);
  });
}
