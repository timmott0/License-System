from PyQt5.QtWidgets import QDialog

class EvalDialog(QDialog):
    def __init__(self, parent=None):
        super(EvalDialog, self).__init__(parent)
        self.setWindowTitle("Evaluation")
        self.resize(400, 300)


