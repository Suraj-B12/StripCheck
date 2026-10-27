import SwiftUI
import PhotosUI
import AVFoundation

private let inkBlue = Color(red: 0.10, green: 0.29, blue: 0.78)

@MainActor
struct GlassCard<Content: View>: View {
    let content: Content
    init(@ViewBuilder content: () -> Content) { self.content = content() }
    var body: some View {
        VStack(alignment: .leading, spacing: 18) { content }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(22)
            .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 28, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: 28).stroke(.white.opacity(0.6), lineWidth: 1))
            .shadow(color: inkBlue.opacity(0.07), radius: 24, y: 10)
    }
}

@MainActor
struct PearlBackground: View {
    var body: some View {
        ZStack {
            Color(uiColor: .systemGroupedBackground)
            LinearGradient(colors: [inkBlue.opacity(0.10), Color.cyan.opacity(0.05), .clear], startPoint: .topLeading, endPoint: .bottomTrailing)
        }.ignoresSafeArea()
    }
}

@MainActor
struct RootView: View {
    @EnvironmentObject private var model: AppModel
    @State private var settings = false
    var body: some View {
        TabView(selection: $model.selectedTab) {
            navigation { CheckView() }.tabItem { Label("Check", systemImage: "viewfinder") }.tag(0)
            navigation { AlertsView() }.tabItem { Label("Alerts", systemImage: "doc.text.magnifyingglass") }.tag(1)
            navigation { CabinetView() }.tabItem { Label("Cabinet", systemImage: "square.stack.3d.up") }.tag(2)
            navigation { ActivityView() }.tabItem { Label("Activity", systemImage: "clock") }.tag(3)
        }
        .sheet(isPresented: $settings) { SettingsView() }
        .safeAreaInset(edge: .top, spacing: 0) {
            if model.busy {
                HStack(spacing: 14) {
                    ProgressView()
                    Text("Checking with your server…").font(.callout)
                    Spacer()
                    Button("Cancel", action: model.cancel)
                }.padding().background(.regularMaterial)
            }
            if let error = model.error {
                HStack(alignment: .top) {
                    Image(systemName: "exclamationmark.circle.fill")
                    Text(error).font(.callout).fixedSize(horizontal: false, vertical: true)
                    Spacer(minLength: 8)
                    Button { model.error = nil } label: { Image(systemName: "xmark") }.accessibilityLabel("Dismiss error")
                }.padding().foregroundStyle(.primary).background(Color.orange.opacity(0.18))
            } else if let notice = model.notice {
                HStack {
                    Text(notice).font(.callout)
                    Spacer()
                    Button { model.notice = nil } label: { Image(systemName: "xmark") }.accessibilityLabel("Dismiss message")
                }.padding().background(.regularMaterial)
            }
        }
        .task { model.refresh() }
    }
    private func navigation<Content: View>(@ViewBuilder content: () -> Content) -> some View {
        NavigationStack {
            content().toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button { settings = true } label: { Image(systemName: "slider.horizontal.3") }
                        .accessibilityLabel("Connection settings")
                }
            }
        }
    }
}

@MainActor
struct CheckView: View {
    @EnvironmentObject private var model: AppModel
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var manual = false
    @State private var samples = false
    var body: some View {
        ZStack {
            PearlBackground()
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    HStack(spacing: 10) {
                        Image(systemName: "circle.hexagongrid.fill").foregroundStyle(inkBlue)
                        Text("A little clarity. A closer check.").font(.headline)
                    }.padding(.top, 8)
                    Text("Know what’s\non the list.").font(.largeTitle.bold()).fixedSize(horizontal: false, vertical: true)
                    Text("Read the batch on your medicine pack. Compare its printed details with the CDSCO alert lists loaded on your computer.")
                        .font(.title3).foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true)
                    GlassCard {
                        HStack {
                            Image(systemName: "pills.fill").font(.system(size: 52, weight: .light)).foregroundStyle(inkBlue)
                                .padding(20).background(.thinMaterial, in: RoundedRectangle(cornerRadius: 24)).accessibilityHidden(true)
                            VStack(alignment: .leading, spacing: 7) {
                                Text("Start with your pack").font(.title2.bold())
                                Text("Batch, product and dates in focus.").foregroundStyle(.secondary)
                            }
                        }
                        PhotoInput(resume: false)
                        Button { manual = true } label: {
                            Label("Type the printed details", systemImage: "keyboard").frame(maxWidth: .infinity).padding(.vertical, 6)
                        }.buttonStyle(.bordered).controlSize(.large)
                        Text("Photos go to the server you choose. The check runs there using its locally stored alert lists.")
                            .font(.callout).foregroundStyle(.secondary)
                    }
                    HStack(alignment: .top) {
                        Image(systemName: "calendar").foregroundStyle(inkBlue)
                        Text("Latest loaded list: \(model.latestMonth)").font(.callout)
                    }
                    if let snapshot = model.snapshot {
                        VStack(spacing: 18) {
                            if !snapshot.fields.batch.isEmpty {
                                GlassCard {
                                    Text(snapshot.demo == true ? "DEMONSTRATION BATCH" : "PRINTED BATCH").font(.headline).foregroundStyle(.secondary)
                                    Text(snapshot.fields.batch).font(.title.monospaced().bold()).textSelection(.enabled)
                                    if !snapshot.fields.product.isEmpty { Text(snapshot.fields.product).font(.title3) }
                                }
                            }
                            if let pending = snapshot.pending { QuestionCard(pending: pending).id("\(snapshot.thread_id)-\(snapshot.history?.count ?? 0)") }
                            if let verdict = snapshot.final { ResultCard(verdict: verdict) }
                            if let warnings = snapshot.warnings, !warnings.isEmpty {
                                GlassCard { ForEach(warnings, id: \.self) { Text($0).font(.callout) } }
                            }
                            if let steps = snapshot.history, !steps.isEmpty {
                                GlassCard {
                                    DisclosureGroup("How this was checked") {
                                        VStack(alignment: .leading, spacing: 18) {
                                            ForEach(steps) { step in
                                                HStack(alignment: .top, spacing: 12) {
                                                    Text(String(step.step ?? 0)).font(.callout.monospaced()).foregroundStyle(inkBlue)
                                                    Text(step.summary).font(.callout)
                                                }
                                            }
                                        }.padding(.top, 16)
                                    }.font(.headline)
                                }
                            }
                        }.transition(.opacity.combined(with: .move(edge: .bottom)))
                    }
                    Button { samples = true } label: {
                        HStack {
                            VStack(alignment: .leading, spacing: 6) {
                                Text("Take a look around").font(.headline)
                                Text("Try 11 clearly marked synthetic examples.").font(.callout).foregroundStyle(.secondary)
                            }
                            Spacer()
                            Image(systemName: "arrow.up.right")
                        }.padding(20).background(.thinMaterial, in: RoundedRectangle(cornerRadius: 24))
                    }.buttonStyle(.plain)
                    Text("A list comparison does not certify a medicine. For questions about a pack, speak with your pharmacist.")
                        .font(.callout).foregroundStyle(.secondary)
                }.padding(22).frame(maxWidth: 760)
                    .animation(reduceMotion ? nil : .spring(response: 0.5, dampingFraction: 0.88), value: model.snapshot?.thread_id)
                    .frame(maxWidth: .infinity)
            }
        }.navigationTitle("StripCheck").navigationBarTitleDisplayMode(.inline)
            .sheet(isPresented: $manual) { ManualEntryView() }
            .sheet(isPresented: $samples) {
                NavigationStack {
                    List(model.demos) { item in
                        Button {
                            samples = false; model.demo(item.id)
                        } label: {
                            VStack(alignment: .leading, spacing: 8) {
                                Text(item.name).font(.headline).foregroundStyle(.primary)
                                Text(item.description).font(.body).foregroundStyle(.secondary)
                                Text("Synthetic demonstration").font(.callout).foregroundStyle(inkBlue)
                            }.padding(.vertical, 8)
                        }
                    }.navigationTitle("Explore examples")
                        .overlay { if model.demos.isEmpty { ContentUnavailableView("Connect to see examples", systemImage: "network", description: Text("Set your server address in connection settings.")) } }
                        .toolbar { Button("Done") { samples = false } }
                }
            }
    }
}

@MainActor
struct PhotoInput: View {
    @EnvironmentObject private var model: AppModel
    let resume: Bool
    @State private var item: PhotosPickerItem?
    @State private var camera = false
    @State private var preview: UIImage?
    @State private var preparedJPEG: Data?
    @State private var photoTask: Task<Void, Never>?
    var body: some View {
        VStack(spacing: 14) {
            ViewThatFits(in: .horizontal) {
                HStack(spacing: 12) { photoButton; cameraButton }
                VStack(spacing: 12) { photoButton; cameraButton }
            }
            if let preview {
                Image(uiImage: preview).resizable().scaledToFit().frame(maxHeight: 220).clipShape(RoundedRectangle(cornerRadius: 18)).accessibilityLabel("Selected pack photo")
                Button(resume ? "Use this carton photo" : "Check this photo") {
                    guard let data = preparedJPEG ?? preview.uploadJPEG() else { model.error = "This photo could not be prepared. Please choose another."; return }
                    model.upload(data, resume: resume); self.preview = nil; preparedJPEG = nil
                }.buttonStyle(.borderedProminent).controlSize(.large).disabled(model.busy)
            }
        }
        .sheet(isPresented: $camera) {
            CameraPicker { image in
                photoTask?.cancel()
                guard let jpeg = image.uploadJPEG(), let thumbnail = UIImage(data: jpeg) else {
                    model.error = "This photo could not be prepared. Please try again."
                    return
                }
                preparedJPEG = jpeg; preview = thumbnail
            }.ignoresSafeArea()
        }
        .onChange(of: item) { _, value in
            photoTask?.cancel()
            preview = nil; preparedJPEG = nil
            photoTask = Task {
                do {
                    guard let value else { return }
                    guard let data = try await value.loadTransferable(type: Data.self) else { throw ImagePreparation.Failure.unreadable }
                    try Task.checkCancellation()
                    let jpeg = try await Task.detached(priority: .userInitiated) { try ImagePreparation.jpeg(from: data) }.value
                    try Task.checkCancellation()
                    guard let image = UIImage(data: jpeg) else { throw ImagePreparation.Failure.unreadable }
                    preparedJPEG = jpeg; preview = image
                } catch is CancellationError { }
                catch { if !Task.isCancelled { model.error = error.localizedDescription } }
            }
        }
        .onDisappear { photoTask?.cancel() }
    }
    private var photoButton: some View {
        PhotosPicker(selection: $item, matching: .images) {
            Label("Choose a photo", systemImage: "photo").frame(maxWidth: .infinity).padding(.vertical, 6)
        }.buttonStyle(.borderedProminent).controlSize(.large)
    }
    private var cameraButton: some View {
        Button {
            Task {
                let allowed = await AVCaptureDevice.requestAccess(for: .video)
                if allowed { camera = true } else { model.error = "Camera access is off. Enable it in iPhone Settings, or choose a photo instead." }
            }
        } label: { Label("Camera", systemImage: "camera").frame(maxWidth: .infinity).padding(.vertical, 6) }
            .buttonStyle(.bordered).controlSize(.large).disabled(!UIImagePickerController.isSourceTypeAvailable(.camera))
    }
}

@MainActor
struct FieldEditor: View {
    @Binding var fields: PackFields
    var includeBatch = true
    var body: some View {
        if includeBatch { TextField("Batch number", text: $fields.batch).textInputAutocapitalization(.characters).autocorrectionDisabled() }
        TextField("Product name", text: $fields.product)
        TextField("Brand, if printed", text: $fields.brand)
        TextField("Manufacturer", text: $fields.maker)
        TextField("Manufactured, e.g. 08/2024", text: $fields.mfg).autocorrectionDisabled()
        TextField("Expiry, e.g. 07/2027", text: $fields.exp).autocorrectionDisabled()
    }
}

@MainActor
struct ManualEntryView: View {
    @EnvironmentObject private var model: AppModel
    @Environment(\.dismiss) private var dismiss
    @State private var fields = PackFields()
    var body: some View {
        NavigationStack {
            Form {
                Section { FieldEditor(fields: $fields) } header: { Text("Copy from the pack") } footer: { Text("A product name and manufacturer or dates help distinguish batches that share a code. Enter only the details you can read.") }
                Button("Check this batch") { model.check(fields); dismiss() }.disabled(fields.batch.trimmingCharacters(in: .whitespaces).isEmpty).frame(maxWidth: .infinity)
            }.navigationTitle("Printed details").navigationBarTitleDisplayMode(.inline)
                .toolbar { ToolbarItem(placement: .cancellationAction) { Button("Cancel") { dismiss() } } }
        }
    }
}

@MainActor
struct QuestionCard: View {
    @EnvironmentObject private var model: AppModel
    let pending: Pending
    @State private var typed = ""
    @State private var details = PackFields()
    var body: some View {
        GlassCard {
            Label("A closer look", systemImage: "hand.point.up.left").font(.title2.bold())
            Text(pending.question).font(.title3).fixedSize(horizontal: false, vertical: true)
            if let error = pending.error { Text(error).foregroundStyle(.orange).font(.callout) }
            if ["confirm_batch", "type_batch"].contains(pending.kind) {
                TextField("Type the whole printed batch", text: $typed).font(.title3.monospaced()).textInputAutocapitalization(.characters).autocorrectionDisabled().textFieldStyle(.roundedBorder)
                Button("Confirm printed batch") { model.answer(["typed": .string(typed)]) }.buttonStyle(.borderedProminent).controlSize(.large).disabled(typed.trimmingCharacters(in: .whitespaces).isEmpty || model.busy)
            } else if pending.kind == "box_photo" {
                PhotoInput(resume: true)
                DisclosureGroup("Enter printed details") {
                    VStack(spacing: 14) {
                        FieldEditor(fields: $details, includeBatch: false).textFieldStyle(.roundedBorder)
                        Button("Use these details") { model.answer(["fields": .object(details.payload)]) }.buttonStyle(.borderedProminent).controlSize(.large).disabled(model.busy || [details.product, details.brand, details.maker, details.mfg, details.exp].allSatisfy { $0.isEmpty })
                    }.padding(.top, 14)
                }
            } else {
                ForEach((pending.options ?? []).filter { !["can't tell", "cant_tell"].contains($0.lowercased()) }, id: \.self) { option in
                    Button { model.answer(["choice": .string(option)]) } label: { Text(option).font(.title3).frame(maxWidth: .infinity, alignment: .leading).padding(.vertical, 4) }
                        .buttonStyle(.bordered).controlSize(.large).disabled(model.busy)
                }
            }
            Button("I can’t tell") { model.answer(["skip": .bool(true)]) }.controlSize(.large).disabled(model.busy)
        }
    }
}

@MainActor
struct ResultCard: View {
    @EnvironmentObject private var model: AppModel
    let verdict: Verdict
    var allowSave = true
    private var tone: Color { ["FLAGGED", "SUSPECTED_FAKE"].contains(verdict.label) ? .red : verdict.label == "NOT_LISTED" ? inkBlue : .orange }
    var body: some View {
        GlassCard {
            Image(systemName: ["FLAGGED", "SUSPECTED_FAKE"].contains(verdict.label) ? "exclamationmark.triangle.fill" : verdict.label == "NOT_LISTED" ? "doc.text.magnifyingglass" : "questionmark.circle.fill").font(.largeTitle).foregroundStyle(tone).accessibilityHidden(true)
            Text(verdict.headline).font(.title2.bold()).fixedSize(horizontal: false, vertical: true)
            Text(verdict.explanation).font(.title3).textSelection(.enabled)
            if let advice = verdict.advice { Text(advice).font(.body).foregroundStyle(.secondary) }
            if let evidence = verdict.evidence, !evidence.isEmpty {
                VStack(spacing: 10) {
                    ForEach(evidence.keys.sorted(), id: \.self) { key in
                        HStack { Text(key.capitalized); Spacer(); Text((evidence[key] ?? "").replacingOccurrences(of: "_", with: " ")).foregroundStyle(.secondary) }.font(.callout)
                    }
                }.padding(16).background(.thinMaterial, in: RoundedRectangle(cornerRadius: 18))
            }
            ForEach(verdict.citations ?? []) { citation in
                VStack(alignment: .leading, spacing: 8) {
                    Text(citation.text ?? citation.title ?? "Source record").font(.callout).textSelection(.enabled)
                    if let url = citation.link { Link(destination: url) { Label("Open official source", systemImage: "arrow.up.right.square") }.font(.body) }
                }
            }
            if allowSave {
                Button { model.savePack() } label: { Label("Save to cabinet", systemImage: "bookmark").frame(maxWidth: .infinity).padding(.vertical, 4) }
                    .buttonStyle(.bordered).controlSize(.large).disabled(model.busy || model.snapshot?.fields.batch.isEmpty != false)
            }
        }
    }
}

@MainActor
struct AlertsView: View {
    @EnvironmentObject private var model: AppModel
    @State private var query = ""
    var body: some View {
        List {
            Section { Text("Latest loaded: \(model.latestMonth)").foregroundStyle(.secondary) }
            ForEach(model.alerts) { alert in
                NavigationLink {
                    AlertDetail(alert: alert)
                } label: {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(alert["product"]).font(.headline)
                        Text("Batch \(alert["batch_raw"].isEmpty ? alert["batch_key"] : alert["batch_raw"])").font(.body.monospaced())
                        Text("\(alert["entry_type"]) · \(alert["list_month"])").font(.callout).foregroundStyle(.secondary)
                    }.padding(.vertical, 8)
                }
            }
            if model.alertPages > 1 {
                HStack {
                    Button("Previous") { model.searchAlerts(query, page: model.alertPage - 1) }.disabled(model.alertPage <= 1 || model.busy)
                    Spacer()
                    Text("\(model.alertPage) / \(model.alertPages)").font(.callout)
                    Spacer()
                    Button("Next") { model.searchAlerts(query, page: model.alertPage + 1) }.disabled(model.alertPage >= model.alertPages || model.busy)
                }
            }
        }.navigationTitle("Alert library").searchable(text: $query, prompt: "Product, batch or manufacturer")
            .onSubmit(of: .search) { model.searchAlerts(query) }
            .onChange(of: query) { _, value in if value.isEmpty { model.searchAlerts("") } }
            .refreshable { model.searchAlerts(query) }
            .overlay { if model.alerts.isEmpty && !model.busy { ContentUnavailableView("No alerts to show", systemImage: "doc.text.magnifyingglass", description: Text("Load official CDSCO lists on your computer, or try another search.")) } }
    }
}

@MainActor
struct AlertDetail: View {
    let alert: Record
    var body: some View {
        List {
            Section {
                Text(alert["product"]).font(.title2.bold())
                ForEach([("Batch", "batch_raw"), ("Manufacturer", "maker_name"), ("Manufactured", "mfg"), ("Expiry", "exp"), ("Alert type", "entry_type"), ("List month", "list_month"), ("Reported finding", "result")], id: \.0) { item in
                    VStack(alignment: .leading, spacing: 8) { Text(item.0).font(.headline); Text(alert[item.1].isEmpty ? "Not stated" : alert[item.1]).textSelection(.enabled) }.padding(.vertical, 4)
                }
            }
            if let url = URL(string: alert["source_url"]), ["http", "https"].contains(url.scheme) { Section { Link("Open official source", destination: url) } }
        }.navigationTitle("Source record").navigationBarTitleDisplayMode(.inline)
    }
}

@MainActor
struct CabinetView: View {
    @EnvironmentObject private var model: AppModel
    var body: some View {
        List {
            Section {
                Button { model.recheckCabinet() } label: { Label("Recheck saved packs", systemImage: "arrow.clockwise") }.disabled(model.busy || model.cabinet.isEmpty)
                Text("Saved on your connected server. Rechecks use its currently loaded alert lists.").font(.callout).foregroundStyle(.secondary)
            }
            ForEach(model.cabinet) { item in
                NavigationLink { CabinetDetail(item: item) } label: {
                    VStack(alignment: .leading, spacing: 9) {
                        Text(item["label"]).font(.headline).foregroundStyle(.primary)
                        Text(item.fields["batch"]?.text ?? "").font(.body.monospaced()).foregroundStyle(.primary)
                        Text(item.verdict["headline"]?.text ?? "Awaiting review").font(.callout).foregroundStyle(.secondary)
                        if item.values["demo"] == .bool(true) { Text("Synthetic demonstration").font(.callout).foregroundStyle(inkBlue) }
                    }.padding(.vertical, 8)
                }.swipeActions { Button("Delete", role: .destructive) { model.deletePack(item.id) } }
            }
        }.navigationTitle("Your cabinet").refreshable { model.refresh() }
            .overlay { if model.cabinet.isEmpty && !model.busy { ContentUnavailableView("Keep a pack in view", systemImage: "square.stack.3d.up", description: Text("After a check, save its printed details here to compare them again later.")) } }
    }
}

@MainActor
struct CabinetDetail: View {
    @EnvironmentObject private var model: AppModel
    let item: Record
    private var verdict: Verdict? {
        guard let data = try? JSONEncoder().encode(JSONValue.object(item.verdict)) else { return nil }
        return try? JSONDecoder().decode(Verdict.self, from: data)
    }
    var body: some View {
        ZStack {
            PearlBackground()
            ScrollView {
                VStack(alignment: .leading, spacing: 22) {
                    Text(item.fields["batch"]?.text ?? "").font(.title.monospaced().bold())
                    Text("Last checked: \(item["last_checked"].prefix(10))").font(.callout).foregroundStyle(.secondary)
                    if let verdict { ResultCard(verdict: verdict, allowSave: false) }
                    Button("Open original check") { model.openCheck(item["thread_id"]) }.buttonStyle(.bordered).controlSize(.large)
                }.padding(22)
            }
        }.navigationTitle(item["label"]).navigationBarTitleDisplayMode(.inline)
    }
}

@MainActor
struct ActivityView: View {
    @EnvironmentObject private var model: AppModel
    var body: some View {
        List(model.activity) { check in
            Button { model.openCheck(check.thread_id) } label: {
                VStack(alignment: .leading, spacing: 8) {
                    Text(check.fields.product.isEmpty ? "Pack check" : check.fields.product).font(.headline).foregroundStyle(.primary)
                    Text(check.fields.batch.isEmpty ? "Batch unreadable" : check.fields.batch).font(.body.monospaced()).foregroundStyle(.primary)
                    Text(check.final?.headline ?? (check.status == "waiting" ? "Waiting for your answer" : check.status == "error" ? "This check could not complete" : "Check in progress")).font(.callout).foregroundStyle(.secondary)
                    if let date = check.created_at { Text(date.prefix(10)).font(.callout).foregroundStyle(.secondary) }
                }.padding(.vertical, 8)
            }
        }.navigationTitle("Recent checks").refreshable { model.refresh() }
            .overlay { if model.activity.isEmpty && !model.busy { ContentUnavailableView("Your checks, together", systemImage: "clock", description: Text("Completed and paused checks from your server appear here.")) } }
    }
}

@MainActor
struct SettingsView: View {
    @EnvironmentObject private var model: AppModel
    @Environment(\.dismiss) private var dismiss
    @State private var address = ""
    @State private var token = ""
    @State private var problem: String?
    var body: some View {
        NavigationStack {
            Form {
                Section { Text("Run StripCheck on your computer and keep both devices on the same trusted Wi-Fi. Copy the address from the website’s phone pairing screen.").font(.body) }
                Section("Your server") {
                    TextField("http://computer.local:8000", text: $address).keyboardType(.URL).textInputAutocapitalization(.never).autocorrectionDisabled()
                    SecureField("Pairing token, if enabled", text: $token).textInputAutocapitalization(.never).autocorrectionDisabled()
                    Text("The token is stored in this device’s Keychain. Photos are uploaded only when you choose to check them.").font(.callout).foregroundStyle(.secondary)
                }
                if let problem { Section { Text(problem).foregroundStyle(.red) } }
                Section {
                    Button("Save and connect") {
                        do { try model.saveSettings(address: address, token: token); dismiss() }
                        catch { problem = error.localizedDescription }
                    }
                    Button("Open iPhone Settings") { if let url = URL(string: UIApplication.openSettingsURLString) { UIApplication.shared.open(url) } }
                }
                Section("About this check") { Text("StripCheck compares printed medicine-pack details with stored CDSCO alerts. Its results are limited by the records loaded and the quality of the printed evidence. The app does not certify a medicine.") }
            }.navigationTitle("Connection").navigationBarTitleDisplayMode(.inline)
                .toolbar { ToolbarItem(placement: .cancellationAction) { Button("Done") { dismiss() } } }
                .onAppear { address = model.address; token = model.tokenValue }
        }
    }
}
