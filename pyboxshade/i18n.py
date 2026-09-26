from PyQt5 import sip
from PyQt5.QtCore import QEvent, QObject, QTranslator, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QAction, QAbstractButton, QApplication, QComboBox, QDialog, QGroupBox,
    QLabel, QMenu, QMessageBox, QTabWidget, QTableWidget, QToolBar, QWidget,
    QHeaderView,
)

from pyboxshade.settings import new_settings
from pyboxshade.errors import APP_ERRORS, describe_error


ZH = {
    "pyBoxshade · Alignment workspace": "pyBoxshade · 序列比对工作区",
    "Shaded alignment": "着色预览", "Source alignment": "原始比对",
    "Open an alignment or drag a file into this window.": "打开比对文件，或将文件拖入此窗口。",
    "Open an alignment to begin": "打开比对文件以开始",
    "Open alignment…": "打开比对文件…", "ALIGNMENT WORKSPACE": "序列比对工作区",
    "Ctrl + wheel to zoom\nDrag the preview to pan": "Ctrl + 滚轮缩放\n拖动预览可平移",
    "Protein": "蛋白质", "DNA / RNA": "DNA / RNA", "DNA/RNA": "DNA/RNA",
    "Consensus line": "共识序列行", "Position ruler": "位置标尺",
    "Sequence type": "序列类型", "Threshold": "共识阈值", "Residues / line": "每行位点数",
    "All settings…": "全部设置…", "Shading & layout": "着色与排版",
    "Recent files": "最近打开", "&Export": "导出(&E)",
    "PDF document…": "PDF 文档…", "SVG vector image…": "SVG 矢量图…",
    "PNG image…": "PNG 图片…", "RTF document…": "RTF 文档…",
    "PostScript…": "PostScript 文档…", "Text comparison…": "文本比较…",
    "Preview": "预览", "Fit": "适应窗口", "Zoom +": "放大", "Zoom −": "缩小",
    "Refresh preview": "刷新预览", "&Open...": "打开(&O)…", "E&xit": "退出(&X)",
    "Settings": "设置", "Make RTF": "导出 RTF", "Make PS": "导出 PS",
    "Make Text": "导出文本", "&About": "关于(&A)", "&File": "文件(&F)",
    "&Actions": "操作(&A)", "&Help": "帮助(&H)", "Actions": "操作",
    "Open an existing file": "打开已有文件", "Exit the application": "退出程序",
    "Open dialog to allow control of program settings": "打开全部设置",
    "Make RTF file": "导出 RTF 文件", "Make PS file": "导出 PostScript 文件",
    "Make text file": "导出文本比较文件", "Show image in window": "显示着色预览",
    "Show the application's About box": "查看程序版本及许可",
    "Ready": "就绪", "File loaded": "文件已载入", "Open alignment file": "打开比对文件",
    "Unable to open alignment": "无法打开比对文件", "Export failed": "导出失败",
    "About pyBoxshade": "关于 pyBoxshade", "Invalid reference": "参考序列无效",
    "Reference sequence is outside the alignment.": "参考序列编号超出比对中的序列范围。",
    "General": "常规", "Text (ASCII) output": "文本输出", "Similarities": "相似残基",
    "Groups": "残基分组", "Boxshade Preferences": "pyBoxshade 设置",
    "Consensus to a single sequence": "以指定序列为参考", "Make consensus to sequence:": "参考序列编号：",
    "Print sequence names": "显示序列名称", "Print sequence numbers:": "显示序列编号：",
    "at left end": "左侧", "at right end": "右侧", "Default numbering (start at 1)": "默认编号（从 1 开始）",
    "Seq. No.": "序列编号", "Start number": "起始编号", "Threshold Fraction (0-1):": "共识阈值（0–1）：",
    "Gaps count towards totals": "将缺口计入总数", "Special shading for similar residues": "单独着色相似残基",
    "Special shading for completely\nconserved residues": "单独着色完全保守残基",
    "Print consensus line": "显示共识序列行", "Print ruler line": "显示位置标尺",
    "Symbols for consensus:": "共识符号：", "Sequence characters per line:": "每行位点数：",
    "Number of lines between blocks:": "区块间空行数：", "Invalid consensus symbols": "共识符号无效",
    "Enter exactly three consensus symbols.": "请输入恰好三个共识符号。",
    "Different from consensus": "与共识不同", "Identical to consensus": "与共识相同",
    "Similar to consensus": "与共识相似", "All the same residue": "全部序列一致",
    "Other prefs": "其他设置", "Uppercase": "大写", "Lowercase": "小写",
    "Foreground": "文字颜色", "Background": "背景颜色",
    "Font size:": "字号：", "Portrait": "纵向", "Landscape": "横向",
    "Different: ": "不同：", "Identical: ": "相同：", "Similar:  ": "相似：", "Conserved:": "保守：",
    "Amino Acid": "氨基酸", "Similar to:": "相似残基", "Nucleic Acid": "核苷酸",
    "Amino Acid Groups": "氨基酸分组", "Nucleic Acid Groups": "核苷酸分组",
    "Language": "语言", "OK": "确定", "Cancel": "取消", "&Yes": "是(&Y)", "&No": "否(&N)",
    "Open": "打开", "Save": "保存", "Close": "关闭", "Choose Color": "选择颜色",
    "Show Details...": "显示详细信息…", "Hide Details...": "隐藏详细信息…",
    "&Show Details...": "显示详细信息(&S)…", "&Hide Details...": "隐藏详细信息(&H)…",
    "Look in:": "查找范围：", "File name:": "文件名：", "Files of type:": "文件类型：",
    "Back": "返回", "Forward": "前进", "Parent Directory": "上级目录",
    "Create New Folder": "新建文件夹", "List View": "列表", "Detail View": "详细信息",
    "Name": "名称", "Size": "大小", "Type": "类型", "Date Modified": "修改日期",
    "{count} sequences\n{length:,} positions": "{count} 条序列\n{length:,} 个位点",
    "{count} sequences · {length:,} positions · Ready to export": "{count} 条序列 · {length:,} 个位点 · 可导出",
    "Export {format}": "导出 {format}", "Saved {path}": "已保存：{path}",
    "Preview unavailable: {error}": "无法生成预览：{error}",
    "Unable to allocate preview image.": "无法分配预览图像。",
    "Sequence alignment shading, live preview and vector export.": "序列比对着色、实时预览及矢量导出。",
    "Based on Michael Baron’s pyBoxshade. Licensed under GPL-3.0.": "基于 Michael Baron 的 pyBoxshade，遵循 GPL-3.0 许可。",
}
ZH.update(APP_ERRORS)

# Long explanations live here so the legacy preferences module remains unchanged.
ZH.update({
    "<big><b>Text (ASCII) output is only for comparison to a specific sequence.</b></big><br><br>"
    "In the boxes below, enter the single character to be used to represent residues that are<br>"
    "Different from, Identical to, or Similar to the consensus, or to be used when all sequences<br>"
    "have the same residue (Conserved). Use upper or lowercase 'L' (L or l) to indicate the<br>"
    "character itself or the lower case version of that character<br>":
    "<b>文本输出用于与指定参考序列比较。</b><br><br>"
    "分别输入一个字符，表示与参考不同、相同、相似及完全保守的残基。<br>"
    "输入 L 可保留原字符；输入 l 可输出该字符的小写形式。",
    '<b>Residues to be considered similar for shading purposes</b><br><br>'
    'The "Sims" table allows one to set, for each amino acid (or nucleic acid), which residues are '
    'considered to be similar to it if it is the consensus residue. Each amino acid/base can have '
    'multiple amino acids/bases that are to be considered similar, or none, and amino acids/bases can '
    'appear multiple times on the "similar to" side. The relationship is one way, '
    'e.g. saying that H is similar to a consensus K does not make K similar to a consensus H.':
    '<b>用于相似着色的残基关系</b><br><br>为每一种共识氨基酸或碱基指定相似残基。'
    '可指定多个相似残基，也可留空；同一个残基可在多行出现。关系具有方向性：'
    '将 H 列为共识 K 的相似残基，并不会自动将 K 列为共识 H 的相似残基。',
    '<b>Residues to be considered as groups for shading purposes</b><br><br>'
    'The "Groups" table defines groups of amino acids (or nucleic acids) which are to be considered similar when '
    'establishing a group consensus (e.g. all positive charged, all large hydrophobic, all purines). These '
    'relationships are multiway, e.g. making a group "LMFY" establishes relationships between '
    'all four amino acids.':
    '<b>用于分组着色的残基集合</b><br><br>定义形成组共识时视为相似的氨基酸或碱基集合，'
    '例如带正电的氨基酸、大体积疏水氨基酸或嘌呤。组内关系相互成立：'
    '定义 LMFY 后，四种氨基酸彼此归为同组。',
    "<span style='text-align: center'><p style='font-size: 18pt'>Possible output options error</p></span>":
    "<b>请检查序列编号设置</b>",
    "<p style='font-size: 14pt'> You have selected non-default sequence numbering, but have not set the actual start numbers to be used for each sequence."
    "<br><br>Continue with saving preferences?</p>":
    "已选择自定义序列编号，但各序列起始编号仍为默认值。<br><br>是否继续保存设置？",
})


class StandardTranslator(QTranslator):
    def translate(self, context, source, disambiguation=None, n=-1):
        # Qt's standard buttons and non-native file/color dialogs.
        return ZH.get(source, "")


class InterfaceLanguage(QObject):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.language = "en"
        self.translator = StandardTranslator(self)
        QApplication.instance().installEventFilter(self)

    def text(self, source, **values):
        return (ZH.get(source, source) if self.language == "zh_CN" else source).format(**values)

    def error_text(self, error):
        return describe_error(error, self.language).message

    def show_error(self, title, error):
        report = describe_error(error, self.language)
        dialog = QMessageBox(self.window)
        dialog.setIcon(QMessageBox.Warning)
        dialog.setWindowTitle(self.text(title))
        dialog.setTextFormat(Qt.PlainText)
        dialog.setText(report.message)
        if report.details != report.message:
            dialog.setDetailedText(report.details)
        dialog.setStandardButtons(QMessageBox.Ok)
        return dialog.exec()

    def set_language(self, language):
        if language not in ("zh_CN", "en"):
            raise ValueError(f"Unsupported interface language: {language}")
        app = QApplication.instance()
        app.removeTranslator(self.translator)
        self.language = language
        if language == "zh_CN":
            app.installTranslator(self.translator)
        new_settings().setValue("interfaceLanguage", language)
        self.translate_tree(self.window)

    def replace(self, obj, key, current, setter):
        saved = obj.property("i18n_" + key)
        # Remember sources only when they match the catalogue, avoiding user data.
        if saved and current in (saved, ZH.get(saved, saved)):
            source = saved
        elif current in ZH:
            source = current
            obj.setProperty("i18n_" + key, source)
        else:
            return
        setter(ZH.get(source, source) if self.language == "zh_CN" else source)

    def translate_tree(self, root):
        for obj in [root, *root.findChildren(QWidget), *root.findChildren(QAction)]:
            # QMessageBox text changes can recreate its internal labels/layouts.
            if sip.isdeleted(obj):
                continue
            if obj.property("i18n_skip"):
                continue
            if isinstance(obj, (QLabel, QAbstractButton, QAction)):
                self.replace(obj, "text", obj.text(), obj.setText)
            if isinstance(obj, (QGroupBox, QMenu)):
                self.replace(obj, "title", obj.title(), obj.setTitle)
            if isinstance(obj, QWidget):
                self.replace(obj, "windowTitle", obj.windowTitle(), obj.setWindowTitle)
                self.replace(obj, "toolTip", obj.toolTip(), obj.setToolTip)
                self.replace(obj, "statusTip", obj.statusTip(), obj.setStatusTip)
            if isinstance(obj, QAction):
                self.replace(obj, "toolTip", obj.toolTip(), obj.setToolTip)
                self.replace(obj, "statusTip", obj.statusTip(), obj.setStatusTip)
            if isinstance(obj, QToolBar):
                self.replace(obj, "toolbarTitle", obj.windowTitle(), obj.setWindowTitle)
            if isinstance(obj, QMessageBox):
                self.replace(obj, "message", obj.text(), obj.setText)
                self.replace(obj, "information", obj.informativeText(), obj.setInformativeText)
            if isinstance(obj, QTabWidget):
                for index in range(obj.count()):
                    self.replace(obj, f"tab{index}", obj.tabText(index), lambda text, i=index: obj.setTabText(i, text))
            if isinstance(obj, QComboBox):
                for index in range(obj.count()):
                    self.replace(obj, f"item{index}", obj.itemText(index), lambda text, i=index: obj.setItemText(i, text))
            if isinstance(obj, QTableWidget):
                for index in range(obj.columnCount()):
                    item = obj.horizontalHeaderItem(index)
                    if item:
                        self.replace(obj, f"header{index}", item.text(), item.setText)
            if hasattr(obj, "placeholderText") and hasattr(obj, "setPlaceholderText"):
                self.replace(obj, "placeholder", obj.placeholderText(), obj.setPlaceholderText)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Show and isinstance(obj, QDialog):
            parent = obj.parentWidget()
            while parent is not None and parent is not self.window:
                parent = parent.parentWidget()
            if parent is self.window:
                if obj.windowTitle() in ("Boxshade Preferences", "pyBoxshade 设置"):
                    font = QFont("Segoe UI")
                    font.setPixelSize(14)
                    obj.setFont(font)
                    obj.setFixedWidth(700)
                    for widget in obj.findChildren(QWidget):
                        if isinstance(widget, QLabel) and widget.text() in ("ACGT", "acgt"):
                            sample_font = QFont("Courier New")
                            sample_font.setPixelSize(20)
                            sample_font.setBold(True)
                            widget.setFont(sample_font)
                        else:
                            widget.setFont(font)
                    for label in obj.findChildren(QLabel):
                        label.setWordWrap(len(label.text()) > 100)
                    for table in obj.findChildren(QTableWidget):
                        table.setMaximumWidth(220)
                        table.setMinimumWidth(200)
                        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                self.translate_tree(obj)
        return False
