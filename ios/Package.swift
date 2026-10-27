// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "StripCheckKit",
    platforms: [.macOS(.v13), .iOS(.v17)],
    products: [.library(name: "StripCheckKit", targets: ["StripCheckKit"]), .executable(name: "StripCheckVerify", targets: ["StripCheckVerify"])],
    targets: [
        .target(name: "StripCheckKit"),
        .executableTarget(name: "StripCheckVerify", dependencies: ["StripCheckKit"], path: "Verification"),
        .testTarget(name: "StripCheckKitTests", dependencies: ["StripCheckKit"])
    ]
)
