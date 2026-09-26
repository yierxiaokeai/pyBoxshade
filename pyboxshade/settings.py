from PyQt5.QtCore import QSettings


def new_settings(organization="Boxshade", application="Boxshade"):
    settings = QSettings(QSettings.defaultFormat(), QSettings.UserScope, organization, application)
    settings.setFallbacksEnabled(False)
    return settings
