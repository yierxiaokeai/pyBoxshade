import errno
import re
from dataclasses import dataclass


APP_ERRORS = {
    "The alignment file is empty.": "比对文件为空。",
    "Unrecognised alignment format. Use FASTA, Clustal, MSF, PHYLIP, Nexus or Stockholm.":
    "无法识别比对格式。请使用 FASTA、Clustal、MSF、PHYLIP、Nexus 或 Stockholm。",
    "An alignment must contain at least two sequences.": "比对文件至少需要两条序列。",
    "The alignment contains no residues.": "比对文件中没有残基。",
    "Reference sequence is outside the alignment.": "参考序列编号超出比对中的序列范围。",
    "Open an alignment before exporting.": "请先打开比对文件再导出。",
    "Choose a .svg, .pdf, .png, .rtf, .ps or .txt output file.": "请选择 SVG、PDF、PNG、RTF、PS 或 TXT 输出文件。",
    "Text export needs a reference sequence. Select one in Settings.": "文本导出需要参考序列，请在设置中指定。",
    "Output is too wide. Reduce font size, line width or sequence name length.": "输出过宽，请减小字号、每行位点数或序列名称长度。",
    "SVG is too tall. Use paginated PDF or increase residues per line.": "SVG 高度过大，请使用分页 PDF 或增加每行位点数。",
    "Image is too large. Reduce font size or use paginated PDF export.": "图像过大，请减小字号或使用分页 PDF。",
    "PostScript line is too wide. Reduce residues per line or font size, or use PDF/SVG.":
    "PostScript 每行过宽，请减少每行位点数、减小字号或使用 PDF / SVG。",
    "Unable to initialise vector rendering.": "无法初始化矢量绘制。",
    "Unable to create a PDF page.": "无法创建 PDF 页面。",
    "Unable to prepare output.": "无法准备输出。", "Unable to encode PNG.": "无法编码 PNG 图片。",
    "Unable to write the complete output file.": "输出文件未能完整写入，请检查剩余空间和写入权限。",
    "Unable to allocate preview image.": "无法分配预览图像。",
}

PARSER_ERRORS = {
    "Sequences must all be the same length": "各序列的比对长度不一致，请补齐缺口并检查比对结果。",
    "Sequences have different lengths, or repeated identifier": "序列比对长度不一致，或存在重复标识符，请检查比对长度及序列名称。",
    "No records found in handle": "文件中没有可读取的序列比对记录。",
    "More than one record found in handle": "文件中包含多个比对，请将每个比对分别保存为独立文件。",
    "Must have at least one sequence": "文件中缺少序列记录。",
    "Non-empty sequences are required": "序列内容不能为空。",
    "First line should have two integers": "PHYLIP 首行需要两个整数：序列条数和比对长度。",
    "End of file mid-block": "文件在比对区块中途结束，请检查是否缺少序列行。",
    "Did not find STOCKHOLM header": "缺少有效的 Stockholm 文件头：# STOCKHOLM 1.0。",
    "Unexpected end of file": "文件意外结束，请检查内容是否完整。",
    "Reached end of file without MSF/Type/Check header line": "MSF 文件缺少包含 MSF、Type 和 Check 的文件头。",
    "End of file while looking for end of header // line.": "MSF 文件头缺少结束标记 //。",
    "End of file after // line, expected sequences.": "MSF 文件在 // 后结束，缺少序列数据。",
    "After // line, expected blank line before sequences.": "MSF 的 // 标记与序列数据之间需要空行。",
    "End of file where expecting sequence data.": "文件意外结束，缺少后续序列数据。",
    "PHYLIP format no longer allows dots in sequence":
    "PHYLIP 序列含点号，请将缺口明确写为 - 后再导入。",
    "Nexus formatting error: unmatched [": "Nexus 注释中的左方括号 [ 缺少对应的右方括号 ]。",
    "Nexus formatting error: unmatched ]": "Nexus 注释中的右方括号 ] 缺少对应的左方括号 [。",
    "Unmatched [": "Nexus 注释中的左方括号 [ 缺少对应的右方括号 ]。",
    "Unmatched ]": "Nexus 注释中的右方括号 ] 缺少对应的左方括号 [。",
}

PARSER_PATTERNS = (
    (r"Found (\d+) records in this alignment, told to expect (\d+)", "实际读取 {0} 条序列，文件头声明 {1} 条。"),
    (r"Found a record of length (\d+), should be (\d+)", "序列长度为 {0}，文件头声明长度为 {1}。"),
    (r"Duplicate record identifier: (.+)", "序列标识符重复：{0}"),
    (r"Duplicated ID of (.+)", "序列标识符重复：{0}"),
    (r"Identifiers out of order\? Got '(.+)' but expected '(.+)'", "区块中的序列顺序不一致：读取 {0}，预期 {1}。"),
    (r"Alignment length is (\d+), consensus length is (\d+), (.+)", "比对长度为 {0}，共识注释长度为 {1}；注释：{2}"),
    (r"(.+) is not a known (CLUSTAL|GCG MSF) header: (.+)", "无法识别 {1} 文件头 {0}；可用文件头：{2}"),
    (r"Could not parse line(?:, (bad|invalid) sequence number)?:\n([\s\S]+)", "无法解析序列行，请检查序列名称、残基及位置编号：\n{1}"),
    (r"Could not split line into identifier and sequence:\n([\s\S]+)", "此行缺少可分离的序列名称和序列内容：\n{0}"),
    (r"Unexpected line:\n([\s\S]+)", "发现不符合比对格式的行：\n{0}"),
    (r"Malformed GCG MSF name line: ([\s\S]+)", "MSF 序列名称行格式无效：\n{0}"),
)

OS_ERRORS = {
    errno.ENOENT: "文件或目录不存在，请检查路径是否正确。",
    errno.EACCES: "没有访问权限，请检查文件权限并确认目标目录可写。",
    errno.EPERM: "当前操作被系统禁止，请检查文件权限。",
    errno.EISDIR: "指定路径为文件夹，请选择文件路径。",
    errno.ENOTDIR: "路径中的某一级为文件，请检查目录路径。",
    errno.ENOSPC: "存储空间不足，请释放空间或选择其他保存目录。",
    errno.EROFS: "目标位于只读存储中，请选择可写目录。",
    errno.EEXIST: "目标已存在，无法执行当前文件操作。",
    errno.EBUSY: "文件或设备正被占用，请关闭占用程序后重试。",
    errno.ENAMETOOLONG: "文件路径过长，请缩短名称或选择更浅的目录。",
    errno.EINVAL: "文件路径或操作参数无效，请检查名称和路径。",
    errno.EMFILE: "打开的文件过多，请关闭部分文件后重试。",
    errno.EIO: "存储设备读写失败，请检查设备连接与存储状态。",
}

SYSTEM_TEXT = {
    "Permission denied": OS_ERRORS[errno.EACCES],
    "Access is denied.": OS_ERRORS[errno.EACCES],
    "No such file or directory": OS_ERRORS[errno.ENOENT],
    "The system cannot find the file specified.": OS_ERRORS[errno.ENOENT],
    "The system cannot find the path specified.": OS_ERRORS[errno.ENOENT],
    "No space left on device": OS_ERRORS[errno.ENOSPC],
    "Read-only file system": OS_ERRORS[errno.EROFS],
    "Is a directory": OS_ERRORS[errno.EISDIR],
    "The process cannot access the file because it is being used by another process.":
    "文件正被其他程序占用，请关闭占用程序后重试。",
}


class AlignmentReadError(ValueError):
    def __init__(self, attempts):
        self.attempts = tuple(attempts)
        super().__init__("Unable to read the alignment. Check equal sequence lengths.\n" +
                         "\n".join(f"{fmt}: {type(error).__name__}: {error}" for fmt, error in self.attempts))


class FileOperationError(OSError):
    def __init__(self, path, operation, category, detail):
        self.path = str(path)
        self.operation = operation
        self.category = category
        super().__init__(detail)


def qt_file_error(file, operation):
    from PyQt5.QtCore import QFileDevice
    category = "permission" if file.error() == QFileDevice.PermissionsError else "file"
    return FileOperationError(file.fileName(), operation, category, file.errorString())


@dataclass(frozen=True)
class ErrorReport:
    message: str
    details: str


def parser_message(error):
    source = str(error)
    if isinstance(error, AssertionError):
        return "解析器未通过格式校验，请检查序列列的位置、区块顺序和注释格式；校验详情可在详细信息中查看。"
    if source in PARSER_ERRORS:
        return PARSER_ERRORS[source]
    for pattern, template in PARSER_PATTERNS:
        match = re.fullmatch(pattern, source)
        if match:
            return template.format(*match.groups())
    return "解析器无法读取此内容，请检查文件格式、文件头和序列区块；具体原因可在详细信息中查看。"


def describe_error(error, language="zh_CN"):
    source = str(error)
    if language != "zh_CN":
        return ErrorReport(source, source)
    if isinstance(error, AlignmentReadError):
        message = "无法读取比对文件，请根据以下原因检查内容：\n" + "\n".join(
            f"{fmt}：{parser_message(cause)}" for fmt, cause in error.attempts)
    elif isinstance(error, UnicodeDecodeError):
        message = f"文件无法按 {error.encoding} 解码（字节位置 {error.start}）。请将文件保存为 UTF-8 编码后重新打开。"
    elif isinstance(error, UnicodeEncodeError):
        message = f"字符无法使用 {error.encoding} 编码，请检查文本编码设置。"
    elif isinstance(error, FileOperationError):
        reason = OS_ERRORS[errno.EACCES] if error.category == "permission" else SYSTEM_TEXT.get(source)
        action = {"open": "打开输出文件", "write": "写入输出文件", "commit": "保存输出文件"}.get(error.operation, "完成文件操作")
        message = f"无法{action}。\n{reason or '请检查目标目录、文件权限、占用状态及剩余空间。'}\n路径：{error.path}"
        source += f"\nPath: {error.path}\nOperation: {error.operation}"
    elif isinstance(error, OSError):
        winerror = getattr(error, "winerror", None)
        if source in APP_ERRORS:
            message = APP_ERRORS[source]
        elif winerror in (32, 33):
            message = "文件正被其他程序占用，请关闭占用程序后重试。"
        elif winerror == 123:
            message = "文件名称或路径无效，请检查名称中的特殊字符。"
        else:
            message = OS_ERRORS.get(error.errno, SYSTEM_TEXT.get(source, "文件读写失败，请检查路径、权限及存储状态。"))
        if error.filename:
            message += f"\n路径：{error.filename}"
        if error.filename2:
            message += f"\n目标路径：{error.filename2}"
    elif source in APP_ERRORS:
        message = APP_ERRORS[source]
    elif source.startswith("Unsupported residue symbols:"):
        message = "不支持的残基符号：" + source[len("Unsupported residue symbols:"):]
    elif source in PARSER_ERRORS or any(re.fullmatch(pattern, source) for pattern, _ in PARSER_PATTERNS):
        message = parser_message(error)
    else:
        message = "操作未能完成，请查看详细信息中的具体原因。"
    return ErrorReport(message, source)
