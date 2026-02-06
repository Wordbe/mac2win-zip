import Cocoa
import FinderSync

class FinderSync: FIFinderSync {

    override init() {
        super.init()

        let finderSync = FIFinderSyncController.default()
        if let mountedVolumes = FileManager.default.mountedVolumeURLs(
            includingResourceValuesForKeys: nil,
            options: [.skipHiddenVolumes]
        ) {
            finderSync.directoryURLs = Set(mountedVolumes)
        }

        let volumeMonitor = NSWorkspace.shared.notificationCenter
        volumeMonitor.addObserver(
            self,
            selector: #selector(volumesChanged(_:)),
            name: NSWorkspace.didMountNotification,
            object: nil
        )
        volumeMonitor.addObserver(
            self,
            selector: #selector(volumesChanged(_:)),
            name: NSWorkspace.didUnmountNotification,
            object: nil
        )
    }

    @objc private func volumesChanged(_ notification: Notification) {
        let finderSync = FIFinderSyncController.default()
        if let mountedVolumes = FileManager.default.mountedVolumeURLs(
            includingResourceValuesForKeys: nil,
            options: [.skipHiddenVolumes]
        ) {
            finderSync.directoryURLs = Set(mountedVolumes)
        }
    }

    override func menu(for menuKind: FIMenuKind) -> NSMenu {
        let menu = NSMenu(title: "")

        switch menuKind {
        case .contextualMenuForItems, .contextualMenuForContainer:
            let item = NSMenuItem(
                title: "mac2win 압축",
                action: #selector(compressWithMac2Win(_:)),
                keyEquivalent: ""
            )
            item.image = NSImage(systemSymbolName: "doc.zipper", accessibilityDescription: nil)
            menu.addItem(item)
        default:
            break
        }

        return menu
    }

    @objc func compressWithMac2Win(_ sender: AnyObject?) {
        let urls = selectedPaths()
        guard !urls.isEmpty else { return }

        DispatchQueue.global(qos: .userInitiated).async {
            self.runMac2WinZip(urls: urls)
        }
    }

    private func selectedPaths() -> [URL] {
        if let items = FIFinderSyncController.default().selectedItemURLs(), !items.isEmpty {
            return items
        }
        if let target = FIFinderSyncController.default().targetedURL() {
            return [target]
        }
        return []
    }

    private func runMac2WinZip(urls: [URL]) {
        let paths = [
            "\(NSHomeDirectory())/.local/bin",
            "/opt/homebrew/bin",
            "/usr/local/bin"
        ]
        let currentPath = ProcessInfo.processInfo.environment["PATH"] ?? "/usr/bin:/bin"
        let fullPath = (paths + [currentPath]).joined(separator: ":")

        let binaryPath = findBinary("mac2win-zip", in: paths) ?? findBinary("mac2win-zip", in: currentPath.components(separatedBy: ":"))

        guard let mac2winPath = binaryPath else {
            showError("mac2win-zip이 설치되어 있지 않습니다.\n\n설치: pip install mac2win-zip\n또는: uv tool install mac2win-zip")
            return
        }

        let parentDir = urls[0].deletingLastPathComponent().path
        let output: String

        if urls.count == 1 {
            let name = urls[0].lastPathComponent
            var isDir: ObjCBool = false
            FileManager.default.fileExists(atPath: urls[0].path, isDirectory: &isDir)
            if isDir.boolValue {
                output = "\(parentDir)/\(name).zip"
            } else {
                let stem = (name as NSString).deletingPathExtension
                output = "\(parentDir)/\(stem).zip"
            }
        } else {
            output = "\(parentDir)/archive.zip"
        }

        let finalOutput = uniquePath(output)

        let process = Process()
        process.executableURL = URL(fileURLWithPath: mac2winPath)
        process.arguments = urls.map { $0.path } + ["-o", finalOutput]
        process.environment = ProcessInfo.processInfo.environment
        process.environment?["PATH"] = fullPath

        let errorPipe = Pipe()
        process.standardError = errorPipe

        do {
            try process.run()
            process.waitUntilExit()

            if process.terminationStatus == 0 {
                let zipName = (finalOutput as NSString).lastPathComponent
                showNotification("압축 완료: \(zipName)")
                revealInFinder(finalOutput)
            } else {
                let errorData = errorPipe.fileHandleForReading.readDataToEndOfFile()
                let errorMsg = String(data: errorData, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
                showError("압축에 실패했습니다.\(errorMsg.isEmpty ? "" : "\n\n\(errorMsg)")")
            }
        } catch {
            showError("mac2win-zip 실행에 실패했습니다.\n\n\(error.localizedDescription)")
        }
    }

    private func findBinary(_ name: String, in dirs: [String]) -> String? {
        for dir in dirs {
            let path = "\(dir)/\(name)"
            if FileManager.default.isExecutableFile(atPath: path) {
                return path
            }
        }
        return nil
    }

    private func uniquePath(_ path: String) -> String {
        guard FileManager.default.fileExists(atPath: path) else { return path }
        let base = (path as NSString).deletingPathExtension
        let ext = (path as NSString).pathExtension
        var count = 1
        while FileManager.default.fileExists(atPath: "\(base) (\(count)).\(ext)") {
            count += 1
        }
        return "\(base) (\(count)).\(ext)"
    }

    private func showNotification(_ message: String) {
        let script = "display notification \"\(message)\" with title \"mac2win 압축\""
        runAppleScript(script)
    }

    private func showError(_ message: String) {
        let escaped = message.replacingOccurrences(of: "\"", with: "\\\"")
        let script = "display alert \"mac2win 압축 - 오류\" message \"\(escaped)\" as critical"
        runAppleScript(script)
    }

    private func revealInFinder(_ path: String) {
        let escaped = path.replacingOccurrences(of: "\"", with: "\\\"")
        let script = """
        tell application "Finder"
            reveal POSIX file "\(escaped)"
            activate
        end tell
        """
        runAppleScript(script)
    }

    private func runAppleScript(_ source: String) {
        DispatchQueue.main.async {
            if let script = NSAppleScript(source: source) {
                var error: NSDictionary?
                script.executeAndReturnError(&error)
            }
        }
    }
}
