"""Generate the dependency-free Xcode project using stable object identifiers."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
objects = {}


def oid(name):
    return hashlib.sha1(name.encode()).hexdigest()[:24].upper()


def add(identifier, **values):
    key = oid(identifier)
    objects[key] = values
    return key


def file(name, path, kind):
    return add(name, isa="PBXFileReference", lastKnownFileType=kind, path=path, sourceTree="<group>")


app_sources = ["StripCheckApp.swift", "AppModel.swift", "Views.swift", "MediaPicker.swift"]
kit_sources = ["Models.swift", "APIClient.swift", "ImagePreparation.swift"]
source_refs = [file("app-" + name, name, "sourcecode.swift") for name in app_sources]
kit_refs = [file("kit-" + name, name, "sourcecode.swift") for name in kit_sources]
source_builds = [add("build-" + ref, isa="PBXBuildFile", fileRef=ref) for ref in source_refs + kit_refs]
privacy = file("privacy", "PrivacyInfo.xcprivacy", "text.xml")
assets = file("assets", "Assets.xcassets", "folder.assetcatalog")
strings = file("en-strings", "en.lproj/Localizable.strings", "text.plist.strings")
localized = add("localized", isa="PBXVariantGroup", children=[strings], name="Localizable.strings", sourceTree="<group>")
resources = add("resources-group", isa="PBXGroup", children=[privacy, assets, localized], path="Resources", sourceTree="<group>")
info = file("info", "Info.plist", "text.plist.xml")
app_group = add("app-group", isa="PBXGroup", children=source_refs + [info, resources], path="StripCheck", sourceTree="<group>")
kit_group = add("kit-group", isa="PBXGroup", children=kit_refs, path="Sources/StripCheckKit", sourceTree="<group>")
product = add("product", isa="PBXFileReference", explicitFileType="wrapper.application", includeInIndex=0, path="StripCheck.app", sourceTree="BUILT_PRODUCTS_DIR")
products = add("products-group", isa="PBXGroup", children=[product], name="Products", sourceTree="<group>")
main_group = add("main-group", isa="PBXGroup", children=[app_group, kit_group, products], sourceTree="<group>")
sources = add("sources", isa="PBXSourcesBuildPhase", buildActionMask=2147483647, files=source_builds, runOnlyForDeploymentPostprocessing=0)
frameworks = add("frameworks", isa="PBXFrameworksBuildPhase", buildActionMask=2147483647, files=[], runOnlyForDeploymentPostprocessing=0)
resource_builds = [add("build-" + ref, isa="PBXBuildFile", fileRef=ref) for ref in [privacy, assets, localized]]
resource_phase = add("resources", isa="PBXResourcesBuildPhase", buildActionMask=2147483647, files=resource_builds, runOnlyForDeploymentPostprocessing=0)
project_configs, target_configs = [], []
for mode in ["Debug", "Release"]:
    project_configs.append(add("project-" + mode, isa="XCBuildConfiguration", name=mode, buildSettings={
        "CLANG_ENABLE_MODULES": "YES", "CLANG_ENABLE_OBJC_ARC": "YES", "SDKROOT": "iphoneos", "IPHONEOS_DEPLOYMENT_TARGET": "17.0",
        "SWIFT_VERSION": "5.0", "DEBUG_INFORMATION_FORMAT": "dwarf" if mode == "Debug" else "dwarf-with-dsym",
        "SWIFT_OPTIMIZATION_LEVEL": "-Onone" if mode == "Debug" else "-O", "SWIFT_ACTIVE_COMPILATION_CONDITIONS": "DEBUG" if mode == "Debug" else "",
    }))
    target_configs.append(add("target-" + mode, isa="XCBuildConfiguration", name=mode, buildSettings={
        "PRODUCT_BUNDLE_IDENTIFIER": "app.stripcheck.local", "PRODUCT_NAME": "$(TARGET_NAME)", "CODE_SIGN_STYLE": "Automatic",
        "CURRENT_PROJECT_VERSION": "1", "MARKETING_VERSION": "1.0.0", "GENERATE_INFOPLIST_FILE": "NO", "INFOPLIST_FILE": "StripCheck/Info.plist",
        "TARGETED_DEVICE_FAMILY": "1,2", "SUPPORTED_PLATFORMS": "iphoneos iphonesimulator", "SUPPORTS_MACCATALYST": "NO",
        "ASSETCATALOG_COMPILER_APPICON_NAME": "AppIcon", "SWIFT_EMIT_LOC_STRINGS": "YES", "ENABLE_PREVIEWS": "YES",
        "LD_RUNPATH_SEARCH_PATHS": ["$(inherited)", "@executable_path/Frameworks"],
    }))
project_config_list = add("project-configs", isa="XCConfigurationList", buildConfigurations=project_configs, defaultConfigurationIsVisible=0, defaultConfigurationName="Release")
target_config_list = add("target-configs", isa="XCConfigurationList", buildConfigurations=target_configs, defaultConfigurationIsVisible=0, defaultConfigurationName="Release")
target = add("target", isa="PBXNativeTarget", buildConfigurationList=target_config_list, buildPhases=[sources, frameworks, resource_phase], buildRules=[], dependencies=[], name="StripCheck", productName="StripCheck", productReference=product, productType="com.apple.product-type.application")
project = add("project", isa="PBXProject", attributes={"BuildIndependentTargetsInParallel": "YES", "LastSwiftUpdateCheck": "1500", "LastUpgradeCheck": "1500", "TargetAttributes": {target: {"CreatedOnToolsVersion": "15.0"}}}, buildConfigurationList=project_config_list, compatibilityVersion="Xcode 14.0", developmentRegion="en", hasScannedForEncodings=0, knownRegions=["en", "Base"], mainGroup=main_group, productRefGroup=products, projectDirPath="", projectRoot="", targets=[target])


def encode(value, level=0):
    indent = "\t" * level
    if isinstance(value, dict):
        return "{\n" + "".join(indent + "\t" + json.dumps(str(key)) + " = " + encode(item, level + 1) + ";\n" for key, item in value.items()) + indent + "}"
    if isinstance(value, list):
        return "(\n" + "".join(indent + "\t" + encode(item, level + 1) + ",\n" for item in value) + indent + ")"
    if isinstance(value, int):
        return str(value)
    return json.dumps(value)


document = {"archiveVersion": 1, "classes": {}, "objectVersion": 56, "objects": objects, "rootObject": project}
destination = ROOT / "StripCheck.xcodeproj"
destination.mkdir(exist_ok=True)
(destination / "project.pbxproj").write_text("// !$*UTF8*$!\n" + encode(document) + "\n", encoding="utf-8")
scheme = f'''<?xml version="1.0" encoding="UTF-8"?>
<Scheme LastUpgradeVersion="1500" version="1.3">
 <BuildAction parallelizeBuildables="YES" buildImplicitDependencies="YES"><BuildActionEntries><BuildActionEntry buildForTesting="YES" buildForRunning="YES" buildForProfiling="YES" buildForArchiving="YES" buildForAnalyzing="YES"><BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="{target}" BuildableName="StripCheck.app" BlueprintName="StripCheck" ReferencedContainer="container:StripCheck.xcodeproj"/></BuildActionEntry></BuildActionEntries></BuildAction>
 <TestAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.IDEFoundation.Launcher.LLDB" shouldUseLaunchSchemeArgsEnv="YES"><Testables/></TestAction>
 <LaunchAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.IDEFoundation.Launcher.LLDB" launchStyle="0" useCustomWorkingDirectory="NO" ignoresPersistentStateOnLaunch="NO" debugDocumentVersioning="YES" debugServiceExtension="internal" allowLocationSimulation="YES"><BuildableProductRunnable runnableDebuggingMode="0"><BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="{target}" BuildableName="StripCheck.app" BlueprintName="StripCheck" ReferencedContainer="container:StripCheck.xcodeproj"/></BuildableProductRunnable></LaunchAction>
 <ProfileAction buildConfiguration="Release" shouldUseLaunchSchemeArgsEnv="YES" savedToolIdentifier="" useCustomWorkingDirectory="NO" debugDocumentVersioning="YES"><BuildableProductRunnable runnableDebuggingMode="0"><BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="{target}" BuildableName="StripCheck.app" BlueprintName="StripCheck" ReferencedContainer="container:StripCheck.xcodeproj"/></BuildableProductRunnable></ProfileAction>
 <AnalyzeAction buildConfiguration="Debug"/><ArchiveAction buildConfiguration="Release" revealArchiveInOrganizer="YES"/>
</Scheme>
'''
scheme_path = destination / "xcshareddata/xcschemes/StripCheck.xcscheme"
scheme_path.parent.mkdir(parents=True, exist_ok=True)
scheme_path.write_text(scheme, encoding="utf-8")
print(f"Generated StripCheck.xcodeproj with {len(source_refs) + len(kit_refs)} Swift sources and three resources.")
