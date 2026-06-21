from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtCore import Qt


class ImageZoom(QLabel):
    """QLabel avec zoom molette et déplacement au clic."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap_original = None
        self._zoom = 1.0
        self._drag_start = None
        self._offset_x = 0
        self._offset_y = 0
        self.setFocusPolicy(Qt.WheelFocus)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMouseTracking(True)

    def setPixmap(self, pixmap):
        self._pixmap_original = pixmap
        self._zoom = 1.0
        self._offset_x = 0
        self._offset_y = 0
        self._update()

    def _update(self):
        print("_update appelé, pixmap:", self._pixmap_original)
        if self._pixmap_original is None:
            return
        w = int(self._pixmap_original.width() * self._zoom)
        h = int(self._pixmap_original.height() * self._zoom)
        scaled = self._pixmap_original.scaled(
            w, h,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        super().setPixmap(scaled)
        self.resize(w, h)

    def wheelEvent(self, event):
        """Zoom avec la molette."""
        delta = event.angleDelta().y()
        factor = 1.15 if delta > 0 else 0.87
        self._zoom = max(0.1, min(self._zoom * factor, 10.0))
        self._update()

    def mousePressEvent(self, event):
        """Début du déplacement."""
        if event.button() == Qt.LeftButton:
            self._drag_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        """Déplacement de l'image."""
        if self._drag_start is not None:
            self._drag_start = event.pos()

    def mouseReleaseEvent(self, event):
        """Fin du déplacement."""
        self._drag_start = None
        self.setCursor(Qt.ArrowCursor)

    def mouseDoubleClickEvent(self, event):
        """Double clic pour remettre le zoom à 1."""
        self._zoom = 1.0
        self._update()