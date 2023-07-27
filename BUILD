load("@bazel_gazelle//:def.bzl", "gazelle")

gazelle(name = "gazelle")

gazelle(
    name = "gazelle-update-repos",
    args = [
        "-from_file=go.mod",
        "-to_macro=deps.bzl%go_dependencies",
        "-prune",
    ],
    command = "update-repos",
)

load("@rules_python//python:defs.bzl", "py_binary")
py_binary(
    name = "server",
    srcs = ["gdm_server.py"],
    deps = [
        ":gdm_service",
    ],
)


proto_library(
    name = "gdm_service",
    srcs = ["proto/gdm.proto"],
    deps = [
        "@com_google_protobuf//:any_proto",
    ]
)


#load("@rules_python//python:defs.bzl", "py_binary")
#load("@rules_proto//proto:defs.bzl", "proto_library")