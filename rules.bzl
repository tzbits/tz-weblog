load("@rules_python//python:py_binary.bzl", "py_binary")
load("@rules_pkg//pkg:tar.bzl", "pkg_tar")

###############################################################################

# TODO: finish hooking up rule parameters to arguments.

def _weblog_index_impl(ctx):
    # Retrieve the file objects
    template_file = ctx.file.template
    weblog_bin = ctx.executable._weblog_bin
    srcs = ctx.files.srcs

    # Declare the output files.
    outputs = []

    # Build the argument list as a standard Python list.
    arguments_list = [
		"make-feed",
        "--page-template",
        template_file.path,
    ]

    indexhtml = ctx.actions.declare_file("index.html")
	arguments_list.append("--output")
    arguments_list.append(indexhtml.path)
	outputs.append(indexhtml)

    for src in srcs:
        out = ctx.actions.declare_file(src.basename.replace(".md", ".html"))
        outputs.append(out)
        arguments_list.append(src.path)

    ctx.actions.run(
        executable=mdlog_bin,
        inputs=[weblog_bin, template_file] + srcs,
        outputs=outputs,
        arguments=arguments_list,
    )

    return [DefaultInfo(files = depset(outputs))]

weblog_index = rule(
    implementation = _weblog_index_impl,
    attrs = {
        "srcs": attr.label_list(
            allow_files = True,
            mandatory = True,
            doc = "The list of 9c files to transpile",
        ),
        "template": attr.label(
            allow_single_file = True,
            mandatory = True,
            doc = "The template file",
        ),
        "_weblog_bin": attr.label(
            executable = True,
            cfg = "exec",
            default = "//python/tz_weblog:weblog",
        ),
    }
)

