import 'dart:ffi';
import 'dart:io';
import 'package:ffi/ffi.dart';

final DynamicLibrary dylib = Platform.isAndroid
    ? DynamicLibrary.open("librust_backend.so")
    : DynamicLibrary.process();

typedef RustHelloFunc = Pointer<Utf8> Function();
typedef RustHello = Pointer<Utf8> Function();

final RustHello rustHello = dylib
    .lookup<NativeFunction<RustHelloFunc>>("rust_hello")
    .asFunction();

String getHelloFromRust() {
  return rustHello().toDartString();
}
