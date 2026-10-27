import Foundation
import ImageIO

public enum ImagePreparation {
    public enum Failure: Error, LocalizedError {
        case tooLarge, unreadable
        public var errorDescription: String? {
            switch self {
            case .tooLarge: return "Choose a photo smaller than 40 MB."
            case .unreadable: return "This photo could not be read. Choose a JPEG, PNG or HEIC image."
            }
        }
    }
    public static func jpeg(from data: Data, maxDimension: Int = 2400) throws -> Data {
        guard data.count <= 40 * 1024 * 1024 else { throw Failure.tooLarge }
        guard let source = CGImageSourceCreateWithData(data as CFData, [kCGImageSourceShouldCache: false] as CFDictionary),
              let image = CGImageSourceCreateThumbnailAtIndex(source, 0, [
                kCGImageSourceCreateThumbnailFromImageAlways: true,
                kCGImageSourceThumbnailMaxPixelSize: max(1, min(maxDimension, 2400)),
                kCGImageSourceCreateThumbnailWithTransform: true,
                kCGImageSourceShouldCacheImmediately: true,
              ] as CFDictionary) else { throw Failure.unreadable }
        let output = NSMutableData()
        guard let destination = CGImageDestinationCreateWithData(output, "public.jpeg" as CFString, 1, nil) else { throw Failure.unreadable }
        CGImageDestinationAddImage(destination, image, [kCGImageDestinationLossyCompressionQuality: 0.88] as CFDictionary)
        guard CGImageDestinationFinalize(destination) else { throw Failure.unreadable }
        return output as Data
    }
}
