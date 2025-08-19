import 'dart:ffi';
import 'dart:io';
import 'package:ffi/ffi.dart';

final DynamicLibrary pcapLib = Platform.isAndroid 
    ? DynamicLibrary.open('libpcap.so')
    : DynamicLibrary.process();
final DynamicLibrary dylib = Platform.isAndroid
    ? DynamicLibrary.open("librust_backend.so")
    : DynamicLibrary.process();

// TESTING EXAMPLE FUNCTION
typedef RustHelloFunc = Pointer<Utf8> Function();
typedef RustHello = Pointer<Utf8> Function();

typedef StartSniffingNative = Pointer<Utf8> Function();
typedef StartSniffingDart = Pointer<Utf8> Function();

typedef FreeStringNative = Void Function(Pointer<Utf8>);
typedef FreeStringDart = void Function(Pointer<Utf8>); // Dart uses `void`

final RustHello rustHello = dylib
    .lookup<NativeFunction<RustHelloFunc>>("rust_hello")
    .asFunction<RustHello>();

final StartSniffingDart startSniffing = dylib
    .lookup<NativeFunction<StartSniffingNative>>('start_sniffing')
    .asFunction<StartSniffingDart>();
    
final FreeStringDart freeString = dylib
    .lookup<NativeFunction<FreeStringNative>>('free_string')
    .asFunction<FreeStringDart>();


String getHelloFromRust() {
  return rustHello().toDartString();
}

// Returns as a string all the packets
String getPacketsFromRust() {
  final ptr = startSniffing();
  final str = ptr.toDartString(); // needs `ffi: ^2.0.0` or higher
  calloc.free(ptr); // Only if you use malloc in Dart side; with Rust, manage separately
  return str;
}