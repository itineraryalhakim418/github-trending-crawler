#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Trending Crawler - Win11 Explorer Style UI
"""

import os
import sys
import json
import threading
import requests

# Fix blurry fonts on Windows high DPI
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

import customtkinter as ctk
from pathlib import Path
from tkinter import ttk, messagebox, filedialog
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, unquote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from github_trending_crawler import GitHubTrendingCrawler
    from search import RepoSearcher
    from config import ConfigManager
except ImportError as e:
    print(f"导入模块失败: {e}")
    sys.exit(1)

# Win11 Light Theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
ctk.set_widget_scaling(1.2)  # 全局放大 20%，改善高 DPI 下字体模糊

# Win11 Explorer Colors
C = {
    'bg': '#f3f3f3',           # Window background
    'sidebar': '#f9f9f9',      # Left sidebar
    'sidebar_hover': '#e8e8e8',# Sidebar hover
    'sidebar_active': '#e0e0e0',# Sidebar active
    'card': '#ffffff',          # Card/panel white
    'border': '#e5e5e5',        # Subtle borders
    'accent': '#0067c0',        # Win11 blue accent
    'accent_hover': '#005a9e',  # Accent hover
    'accent_light': '#e8f4fd',  # Light blue bg
    'green': '#0f7b0f',         # Win11 green
    'green_hover': '#0b5e0b',
    'red': '#c42b1c',           # Win11 red
    'red_hover': '#a61b10',
    'text': '#1a1a1a',          # Main text
    'text2': '#5d5d5d',         # Secondary text
    'text3': '#8a8a8a',         # Dim text
    'icon': '#1a1a1a',          # Icon color
    'divider': '#ebebeb',       # Divider line
    'hover': '#e9e9e9',         # General hover
    'selected': '#cce4f7',      # Selected item
}

F = {}  # Initialized after root window created

# i18n translations
LANG = {
    'zh': {
        'app_title': 'GitHub Trending Crawler',
        'version': 'v2.1.0',
        'trending': '热榜', 'search': '搜索', 'url_dl': '链接下载',
        'gh_dl': 'GitHub下载', 'settings': '设置',
        'time': '时间:', 'language': '语言:', 'count': '数量:',
        'daily': '日榜', 'weekly': '周榜', 'monthly': '月榜',
        'fetch_trending': '获取热榜', 'keyword': '关键词:',
        'btn_search': '搜索', 'single_dl': '单个下载', 'batch_dl': '批量下载',
        'choose_dir': '选择目录', 'save_location': '保存位置:',
        'threads': '线程数:', 'timeout': '超时:',
        'download_progress': '下载进度', 'ready': '就绪',
        'downloading': '下载中...', 'completed': '完成', 'failed': '失败',
        'stopped': '已终止', 'stop': '终止',
        'dl_trending': '下载热榜结果', 'dl_search': '下载搜索结果',
        'dl_json': '从 JSON 下载', 'concurrency': '并发线程:',
        'gh_dl_title': 'GitHub 仓库下载', 'download_dir': '下载目录',
        'browse': '浏览', 'save_settings': '保存设置',
        'config_file': '配置文件:', 'rate_limit_tip': '可选: 配置后 API 速率 10次/分 → 30次/分',
        'enter_keyword': '请输入关键词', 'searching': '搜索: {}...',
        'found_repos': '找到 {} 个仓库', 'no_results': '无结果',
        'fetching_trending': '获取热榜...', 'total_repos': '共 {} 个仓库',
        'rate_limit_msg': 'API 速率限制，请到设置填写 GitHub Token',
        'no_data': '未获取到数据，请稍后再试',
        'batch_title': '批量下载', 'batch_hint': '每行一个链接:',
        'start_download': '开始下载', 'please_fetch': '请先获取热榜',
        'please_search': '请先搜索', 'settings_saved': '设置已保存',
        'error': '错误', 'success': '成功', 'hint': '提示',
        'ui_language': '界面语言', 'translate_engine': '翻译引擎',
        'baidu_appid': '百度 App ID', 'baidu_key': '百度密钥',
        # Detail page
        'repo_detail': '仓库详情', 'author': '作者',
        'desc': '描述', 'stars': 'Stars', 'forks': 'Forks',
        'watchers': 'Watch', 'issues': 'Issues', 'license': 'License',
        'created': '创建时间', 'updated': '更新时间', 'topics': '标签',
        'open_github': '打开 GitHub', 'download_repo': '下载此仓库',
        'readme': 'README', 'loading': '加载中...', 'load_readme': '加载 README',
        'translate_zh_en': '中→英', 'translate_en_zh': '英→中', 'show_original': '显示原文',
        'translating': '翻译中...', 'translate_failed': '翻译失败',
        'open_issues': '开放 Issues', 'no_issues': '暂无 Issues',
        'load_issues': '加载 Issues', 'comments': '评论',
        'click_to_expand': '点击展开', 'by': '作者:',
        'ui_lang_label': '界面语言', 'trans_engine_label': '翻译引擎',
        'baidu_appid_label': '百度 App ID', 'baidu_key_label': '百度密钥',
        'baidu_tip': '百度翻译需要 App ID 和密钥 (免费申请)',
    },
    'en': {
        'app_title': 'GitHub Trending Crawler',
        'version': 'v2.1.0',
        'trending': 'Trending', 'search': 'Search', 'url_dl': 'URL Download',
        'gh_dl': 'GitHub Download', 'settings': 'Settings',
        'time': 'Time:', 'language': 'Language:', 'count': 'Count:',
        'daily': 'Daily', 'weekly': 'Weekly', 'monthly': 'Monthly',
        'fetch_trending': 'Fetch Trending', 'keyword': 'Keyword:',
        'btn_search': 'Search', 'single_dl': 'Single', 'batch_dl': 'Batch',
        'choose_dir': 'Browse', 'save_location': 'Save to:',
        'threads': 'Threads:', 'timeout': 'Timeout:',
        'download_progress': 'Progress', 'ready': 'Ready',
        'downloading': 'Downloading...', 'completed': 'Done', 'failed': 'Failed',
        'stopped': 'Stopped', 'stop': 'Stop',
        'dl_trending': 'Download Trending', 'dl_search': 'Download Search',
        'dl_json': 'From JSON', 'concurrency': 'Threads:',
        'gh_dl_title': 'GitHub Repo Download', 'download_dir': 'Download Dir',
        'browse': 'Browse', 'save_settings': 'Save Settings',
        'config_file': 'Config:', 'rate_limit_tip': 'Optional: API rate 10/min → 30/min with token',
        'enter_keyword': 'Enter keyword', 'searching': 'Searching: {}...',
        'found_repos': 'Found {} repos', 'no_results': 'No results',
        'fetching_trending': 'Fetching...', 'total_repos': '{} repos total',
        'rate_limit_msg': 'API rate limited, set GitHub Token in Settings',
        'no_data': 'No data, try again later',
        'batch_title': 'Batch Download', 'batch_hint': 'One URL per line:',
        'start_download': 'Start Download', 'please_fetch': 'Fetch trending first',
        'please_search': 'Search first', 'settings_saved': 'Settings saved',
        'error': 'Error', 'success': 'Success', 'hint': 'Hint',
        'ui_language': 'Language', 'translate_engine': 'Translate Engine',
        'baidu_appid': 'Baidu App ID', 'baidu_key': 'Baidu Key',
        # Detail page
        'repo_detail': 'Repository Detail', 'author': 'Author',
        'desc': 'Description', 'stars': 'Stars', 'forks': 'Forks',
        'watchers': 'Watch', 'issues': 'Issues', 'license': 'License',
        'created': 'Created', 'updated': 'Updated', 'topics': 'Topics',
        'open_github': 'Open GitHub', 'download_repo': 'Download Repo',
        'readme': 'README', 'loading': 'Loading...', 'load_readme': 'Load README',
        'translate_zh_en': 'ZH→EN', 'translate_en_zh': 'EN→ZH', 'show_original': 'Original',
        'translating': 'Translating...', 'translate_failed': 'Translate failed',
        'open_issues': 'Open Issues', 'no_issues': 'No issues',
        'load_issues': 'Load Issues', 'comments': 'Comments',
        'click_to_expand': 'Click to expand', 'by': 'by',
        'ui_lang_label': 'Language', 'trans_engine_label': 'Translate Engine',
        'baidu_appid_label': 'Baidu App ID', 'baidu_key_label': 'Baidu Key',
        'baidu_tip': 'Baidu Translate requires App ID & Key (free to apply)',
    },
    'ja': {
        'app_title': 'GitHub トレンドクローラー',
        'version': 'v2.1.0',
        'trending': 'トレンド', 'search': '検索', 'url_dl': 'URL ダウンロード',
        'gh_dl': 'GitHub ダウンロード', 'settings': '設定',
        'time': '時間:', 'language': '言語:', 'count': '件数:',
        'daily': '日間', 'weekly': '週間', 'monthly': '月間',
        'fetch_trending': 'トレンド取得', 'keyword': 'キーワード:',
        'btn_search': '検索', 'single_dl': '単一', 'batch_dl': '一括',
        'choose_dir': '参照', 'save_location': '保存先:',
        'threads': 'スレッド:', 'timeout': 'タイムアウト:',
        'download_progress': '進捗', 'ready': '準備完了',
        'downloading': 'ダウンロード中...', 'completed': '完了', 'failed': '失敗',
        'stopped': '中止', 'stop': '中止',
        'dl_trending': 'トレンドDL', 'dl_search': '検索DL',
        'dl_json': 'JSONからDL', 'concurrency': 'スレッド:',
        'gh_dl_title': 'GitHub リポジトリDL', 'download_dir': 'DL先',
        'browse': '参照', 'save_settings': '設定保存',
        'config_file': '設定ファイル:', 'rate_limit_tip': 'オプション: トークンで API 10回/分 → 30回/分',
        'enter_keyword': 'キーワード入力', 'searching': '検索中: {}...',
        'found_repos': '{}件見つかりました', 'no_results': '結果なし',
        'fetching_trending': '取得中...', 'total_repos': '{}件',
        'rate_limit_msg': 'API制限、設定でTokenを入力してください',
        'no_data': 'データなし、後で再試行',
        'batch_title': '一括DL', 'batch_hint': '1行1URL:',
        'start_download': 'DL開始', 'please_fetch': '先にトレンド取得',
        'please_search': '先に検索', 'settings_saved': '設定保存済',
        'error': 'エラー', 'success': '成功', 'hint': 'ヒント',
        'ui_language': '言語', 'translate_engine': '翻訳エンジン',
        'baidu_appid': 'Baidu App ID', 'baidu_key': 'Baidu Key',
        'repo_detail': 'リポジトリ詳細', 'author': '著者',
        'desc': '説明', 'stars': 'Stars', 'forks': 'Forks',
        'watchers': 'Watch', 'issues': 'Issues', 'license': 'ライセンス',
        'created': '作成日', 'updated': '更新日', 'topics': 'トピック',
        'open_github': 'GitHubを開く', 'download_repo': 'リポジトリDL',
        'readme': 'README', 'loading': '読み込み中...', 'load_readme': 'README読込',
        'translate_zh_en': '中→英', 'translate_en_zh': '英→中', 'show_original': '原文表示',
        'translating': '翻訳中...', 'translate_failed': '翻訳失敗',
        'open_issues': 'Open Issues', 'no_issues': 'Issuesなし',
        'load_issues': 'Issues読込', 'comments': 'コメント',
        'click_to_expand': 'クリック展開', 'by': '著者:',
        'ui_lang_label': '言語', 'trans_engine_label': '翻訳エンジン',
        'baidu_appid_label': 'Baidu App ID', 'baidu_key_label': 'Baidu Key',
        'baidu_tip': '百度翻訳はApp IDとKeyが必要 (無料)',
    },
    'ko': {
        'app_title': 'GitHub 트렌드 크롤러',
        'version': 'v2.1.0',
        'trending': '트렌드', 'search': '검색', 'url_dl': 'URL 다운로드',
        'gh_dl': 'GitHub 다운로드', 'settings': '설정',
        'time': '시간:', 'language': '언어:', 'count': '수량:',
        'daily': '일간', 'weekly': '주간', 'monthly': '월간',
        'fetch_trending': '트렌드 가져오기', 'keyword': '키워드:',
        'btn_search': '검색', 'single_dl': '단일', 'batch_dl': '일괄',
        'choose_dir': '찾기', 'save_location': '저장 위치:',
        'threads': '스레드:', 'timeout': '시간초과:',
        'download_progress': '진행률', 'ready': '준비',
        'downloading': '다운로드 중...', 'completed': '완료', 'failed': '실패',
        'stopped': '중지', 'stop': '중지',
        'dl_trending': '트렌드 DL', 'dl_search': '검색 DL',
        'dl_json': 'JSON에서 DL', 'concurrency': '스레드:',
        'gh_dl_title': 'GitHub 저장소 DL', 'download_dir': 'DL 폴더',
        'browse': '찾기', 'save_settings': '설정 저장',
        'config_file': '설정 파일:', 'rate_limit_tip': '선택: 토큰으로 API 10회/분 → 30회/분',
        'enter_keyword': '키워드 입력', 'searching': '검색 중: {}...',
        'found_repos': '{}개 찾음', 'no_results': '결과 없음',
        'fetching_trending': '가져오는 중...', 'total_repos': '{}개',
        'rate_limit_msg': 'API 제한, 설정에서 Token 입력',
        'no_data': '데이터 없음, 나중에 재시도',
        'batch_title': '일괄 DL', 'batch_hint': '줄당 하나의 URL:',
        'start_download': 'DL 시작', 'please_fetch': '먼저 트렌드 가져오기',
        'please_search': '먼저 검색', 'settings_saved': '설정 저장됨',
        'error': '오류', 'success': '성공', 'hint': '힌트',
        'ui_language': '언어', 'translate_engine': '번역 엔진',
        'baidu_appid': 'Baidu App ID', 'baidu_key': 'Baidu Key',
        'repo_detail': '저장소 상세', 'author': '작성자',
        'desc': '설명', 'stars': 'Stars', 'forks': 'Forks',
        'watchers': 'Watch', 'issues': 'Issues', 'license': '라이선스',
        'created': '생성일', 'updated': '업데이트', 'topics': '토픽',
        'open_github': 'GitHub 열기', 'download_repo': '저장소 DL',
        'readme': 'README', 'loading': '로딩 중...', 'load_readme': 'README 로드',
        'translate_zh_en': '중→영', 'translate_en_zh': '영→중', 'show_original': '원문',
        'translating': '번역 중...', 'translate_failed': '번역 실패',
        'open_issues': 'Open Issues', 'no_issues': 'Issues 없음',
        'load_issues': 'Issues 로드', 'comments': '댓글',
        'click_to_expand': '클릭 확장', 'by': '작성자:',
        'ui_lang_label': '언어', 'trans_engine_label': '번역 엔진',
        'baidu_appid_label': 'Baidu App ID', 'baidu_key_label': 'Baidu Key',
        'baidu_tip': '百度 번역은 App ID와 Key 필요 (무료)',
    },
    'fr': {
        'app_title': 'GitHub Trending Crawler',
        'version': 'v2.1.0',
        'trending': 'Tendances', 'search': 'Recherche', 'url_dl': 'URL Téléchargement',
        'gh_dl': 'GitHub Téléchargement', 'settings': 'Paramètres',
        'time': 'Temps:', 'language': 'Langue:', 'count': 'Nombre:',
        'daily': 'Quotidien', 'weekly': 'Hebdomadaire', 'monthly': 'Mensuel',
        'fetch_trending': 'Tendances', 'keyword': 'Mot-clé:',
        'btn_search': 'Chercher', 'single_dl': 'Unique', 'batch_dl': 'Lot',
        'choose_dir': 'Parcourir', 'save_location': 'Sauvegarder:',
        'threads': 'Threads:', 'timeout': 'Délai:',
        'download_progress': 'Progrès', 'ready': 'Prêt',
        'downloading': 'Téléchargement...', 'completed': 'Terminé', 'failed': 'Échoué',
        'stopped': 'Arrêté', 'stop': 'Arrêter',
        'dl_trending': 'DL Tendances', 'dl_search': 'DL Recherche',
        'dl_json': 'Depuis JSON', 'concurrency': 'Threads:',
        'gh_dl_title': 'DL Dépôt GitHub', 'download_dir': 'Dossier DL',
        'browse': 'Parcourir', 'save_settings': 'Enregistrer',
        'config_file': 'Config:', 'rate_limit_tip': 'Optionnel: API 10/min → 30/min avec token',
        'enter_keyword': 'Entrez mot-clé', 'searching': 'Recherche: {}...',
        'found_repos': '{} dépôts trouvés', 'no_results': 'Aucun résultat',
        'fetching_trending': 'Chargement...', 'total_repos': '{} dépôts',
        'rate_limit_msg': 'Limite API, configurez Token dans Paramètres',
        'no_data': 'Pas de données, réessayez plus tard',
        'batch_title': 'Téléchargement par lot', 'batch_hint': 'Une URL par ligne:',
        'start_download': 'Démarrer', 'please_fetch': 'D\'abord tendances',
        'please_search': 'D\'abord recherche', 'settings_saved': 'Paramètres sauvegardés',
        'error': 'Erreur', 'success': 'Succès', 'hint': 'Info',
        'ui_language': 'Langue', 'translate_engine': 'Moteur de traduction',
        'baidu_appid': 'Baidu App ID', 'baidu_key': 'Baidu Key',
        'repo_detail': 'Détails du dépôt', 'author': 'Auteur',
        'desc': 'Description', 'stars': 'Stars', 'forks': 'Forks',
        'watchers': 'Watch', 'issues': 'Issues', 'license': 'Licence',
        'created': 'Créé', 'updated': 'Mis à jour', 'topics': 'Sujets',
        'open_github': 'Ouvrir GitHub', 'download_repo': 'Télécharger',
        'readme': 'README', 'loading': 'Chargement...', 'load_readme': 'Charger README',
        'translate_zh_en': 'ZH→EN', 'translate_en_zh': 'EN→FR', 'show_original': 'Original',
        'translating': 'Traduction...', 'translate_failed': 'Échec traduction',
        'open_issues': 'Issues Ouvertes', 'no_issues': 'Aucune issue',
        'load_issues': 'Charger Issues', 'comments': 'Commentaires',
        'click_to_expand': 'Cliquer', 'by': 'par',
        'ui_lang_label': 'Langue', 'trans_engine_label': 'Traduction',
        'baidu_appid_label': 'Baidu App ID', 'baidu_key_label': 'Baidu Key',
        'baidu_tip': 'Baidu nécessite App ID & Key (gratuit)',
    },
    'de': {
        'app_title': 'GitHub Trending Crawler',
        'version': 'v2.1.0',
        'trending': 'Trends', 'search': 'Suche', 'url_dl': 'URL Download',
        'gh_dl': 'GitHub Download', 'settings': 'Einstellungen',
        'time': 'Zeit:', 'language': 'Sprache:', 'count': 'Anzahl:',
        'daily': 'Täglich', 'weekly': 'Wöchentlich', 'monthly': 'Monatlich',
        'fetch_trending': 'Trends laden', 'keyword': 'Stichwort:',
        'btn_search': 'Suchen', 'single_dl': 'Einzel', 'batch_dl': 'Stapel',
        'choose_dir': 'Durchsuchen', 'save_location': 'Speichern:',
        'threads': 'Threads:', 'timeout': 'Timeout:',
        'download_progress': 'Fortschritt', 'ready': 'Bereit',
        'downloading': 'Herunterladen...', 'completed': 'Fertig', 'failed': 'Fehlgeschlagen',
        'stopped': 'Gestoppt', 'stop': 'Stopp',
        'dl_trending': 'Trends DL', 'dl_search': 'Suche DL',
        'dl_json': 'Aus JSON', 'concurrency': 'Threads:',
        'gh_dl_title': 'GitHub Repo DL', 'download_dir': 'DL Ordner',
        'browse': 'Durchsuchen', 'save_settings': 'Speichern',
        'config_file': 'Config:', 'rate_limit_tip': 'Optional: API 10/min → 30/min mit Token',
        'enter_keyword': 'Stichwort eingeben', 'searching': 'Suche: {}...',
        'found_repos': '{} Repos gefunden', 'no_results': 'Keine Ergebnisse',
        'fetching_trending': 'Laden...', 'total_repos': '{} Repos',
        'rate_limit_msg': 'API Limit, Token in Einstellungen',
        'no_data': 'Keine Daten, später erneut',
        'batch_title': 'Stapel-Download', 'batch_hint': 'Eine URL pro Zeile:',
        'start_download': 'Starten', 'please_fetch': 'Zuerst Trends laden',
        'please_search': 'Zuerst suchen', 'settings_saved': 'Einstellungen gespeichert',
        'error': 'Fehler', 'success': 'Erfolg', 'hint': 'Hinweis',
        'ui_language': 'Sprache', 'translate_engine': 'Übersetzer',
        'baidu_appid': 'Baidu App ID', 'baidu_key': 'Baidu Key',
        'repo_detail': 'Repo Details', 'author': 'Autor',
        'desc': 'Beschreibung', 'stars': 'Stars', 'forks': 'Forks',
        'watchers': 'Watch', 'issues': 'Issues', 'license': 'Lizenz',
        'created': 'Erstellt', 'updated': 'Aktualisiert', 'topics': 'Themen',
        'open_github': 'GitHub öffnen', 'download_repo': 'Repo herunterladen',
        'readme': 'README', 'loading': 'Laden...', 'load_readme': 'README laden',
        'translate_zh_en': 'ZH→EN', 'translate_en_zh': 'EN→DE', 'show_original': 'Original',
        'translating': 'Übersetzen...', 'translate_failed': 'Übersetzung fehlgeschlagen',
        'open_issues': 'Offene Issues', 'no_issues': 'Keine Issues',
        'load_issues': 'Issues laden', 'comments': 'Kommentare',
        'click_to_expand': 'Klicken', 'by': 'von',
        'ui_lang_label': 'Sprache', 'trans_engine_label': 'Übersetzer',
        'baidu_appid_label': 'Baidu App ID', 'baidu_key_label': 'Baidu Key',
        'baidu_tip': 'Baidu braucht App ID & Key (kostenlos)',
    },
    'es': {
        'app_title': 'GitHub Trending Crawler',
        'version': 'v2.1.0',
        'trending': 'Tendencias', 'search': 'Buscar', 'url_dl': 'URL Descarga',
        'gh_dl': 'GitHub Descarga', 'settings': 'Configuración',
        'time': 'Tiempo:', 'language': 'Idioma:', 'count': 'Cantidad:',
        'daily': 'Diario', 'weekly': 'Semanal', 'monthly': 'Mensual',
        'fetch_trending': 'Obtener Tendencias', 'keyword': 'Palabra clave:',
        'btn_search': 'Buscar', 'single_dl': 'Único', 'batch_dl': 'Lote',
        'choose_dir': 'Examinar', 'save_location': 'Guardar en:',
        'threads': 'Hilos:', 'timeout': 'Tiempo:',
        'download_progress': 'Progreso', 'ready': 'Listo',
        'downloading': 'Descargando...', 'completed': 'Completado', 'failed': 'Fallido',
        'stopped': 'Detenido', 'stop': 'Detener',
        'dl_trending': 'DL Tendencias', 'dl_search': 'DL Búsqueda',
        'dl_json': 'Desde JSON', 'concurrency': 'Hilos:',
        'gh_dl_title': 'DL Repo GitHub', 'download_dir': 'Carpeta DL',
        'browse': 'Examinar', 'save_settings': 'Guardar',
        'config_file': 'Config:', 'rate_limit_tip': 'Opcional: API 10/min → 30/min con token',
        'enter_keyword': 'Ingrese palabra', 'searching': 'Buscando: {}...',
        'found_repos': '{} repos encontrados', 'no_results': 'Sin resultados',
        'fetching_trending': 'Cargando...', 'total_repos': '{} repos',
        'rate_limit_msg': 'Límite API, configura Token en Configuración',
        'no_data': 'Sin datos, intenta después',
        'batch_title': 'Descarga por lotes', 'batch_hint': 'Una URL por línea:',
        'start_download': 'Iniciar', 'please_fetch': 'Primero tendencias',
        'please_search': 'Primero buscar', 'settings_saved': 'Configuración guardada',
        'error': 'Error', 'success': 'Éxito', 'hint': 'Info',
        'ui_language': 'Idioma', 'translate_engine': 'Traductor',
        'baidu_appid': 'Baidu App ID', 'baidu_key': 'Baidu Key',
        'repo_detail': 'Detalle del Repo', 'author': 'Autor',
        'desc': 'Descripción', 'stars': 'Stars', 'forks': 'Forks',
        'watchers': 'Watch', 'issues': 'Issues', 'license': 'Licencia',
        'created': 'Creado', 'updated': 'Actualizado', 'topics': 'Temas',
        'open_github': 'Abrir GitHub', 'download_repo': 'Descargar Repo',
        'readme': 'README', 'loading': 'Cargando...', 'load_readme': 'Cargar README',
        'translate_zh_en': 'ZH→EN', 'translate_en_zh': 'EN→ES', 'show_original': 'Original',
        'translating': 'Traduciendo...', 'translate_failed': 'Traducción fallida',
        'open_issues': 'Issues Abiertos', 'no_issues': 'Sin issues',
        'load_issues': 'Cargar Issues', 'comments': 'Comentarios',
        'click_to_expand': 'Clic para expandir', 'by': 'por',
        'ui_lang_label': 'Idioma', 'trans_engine_label': 'Traductor',
        'baidu_appid_label': 'Baidu App ID', 'baidu_key_label': 'Baidu Key',
        'baidu_tip': 'Baidu requiere App ID y Key (gratis)',
    },
}


class Win11NavButton(ctk.CTkButton):
    """Win11 Explorer style navigation button."""
    def __init__(self, master, text, icon, command=None, **kw):
        super().__init__(master, text=f"  {icon}   {text}", command=command,
                         fg_color='transparent', hover_color=C['sidebar_hover'],
                         anchor='w', height=32, corner_radius=6,
                         font=F['nav'], text_color=C['text'], **kw)
        self._active = False

    def set_active(self, active):
        self._active = active
        if active:
            self.configure(fg_color=C['sidebar_active'], font=F['nav_active'])
        else:
            self.configure(fg_color='transparent', font=F['nav'])


class GitHubCrawlerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GitHub Trending Crawler")
        self.geometry("1400x800")
        self.minsize(1100, 650)
        self.configure(fg_color=C['bg'])

        icon_path = Path(__file__).parent / "icon.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        self.config = ConfigManager()
        token = self.config.get_github_token() or None
        self.crawler = GitHubTrendingCrawler(token=token)
        self.searcher = RepoSearcher(token=token)
        self.lang = self.config.get_ui_language()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.current_repos = []
        self.is_downloading = False
        self.download_cancel = False
        self.current_repo_url = ""
        self.nav_buttons = {}

        # Init fonts after root window exists
        F.update({
            'title': ctk.CTkFont(size=16, weight="normal"),
            'heading': ctk.CTkFont(size=15, weight="bold"),
            'body': ctk.CTkFont(size=14),
            'small': ctk.CTkFont(size=13),
            'caption': ctk.CTkFont(size=12),
            'nav': ctk.CTkFont(size=14),
            'nav_active': ctk.CTkFont(size=14, weight="bold"),
        })

        self._build_ui()
        self.load_config()

    def _on_close(self):
        self.download_cancel = True
        self.is_downloading = False
        self.destroy()
        os._exit(0)

    def _build_ui(self):
        # Main layout: sidebar + content
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()

        # Content area
        self.content = ctk.CTkFrame(self, fg_color=C['bg'], corner_radius=0)
        self.content.grid(row=0, column=1, sticky='nsew')
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # Pages
        self.pages = {}
        for name in ['trending', 'search', 'url_dl', 'gh_dl', 'settings']:
            page = ctk.CTkFrame(self.content, fg_color=C['bg'], corner_radius=0)
            page.grid(row=0, column=0, sticky='nsew')
            self.pages[name] = page

        self._build_trending_page()
        self._build_search_page()
        self._build_url_page()
        self._build_gh_page()
        self._build_settings_page()

        # Status bar
        self.status_frame = ctk.CTkFrame(self, fg_color=C['card'], corner_radius=0,
                                          height=28, border_width=1, border_color=C['divider'])
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky='ew')
        self.status_var = ctk.StringVar(value=self._t('ready'))
        ctk.CTkLabel(self.status_frame, textvariable=self.status_var,
                     font=F['caption'], text_color=C['text3']).pack(side='left', padx=12)

        self._show_page('trending')

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, fg_color=C['sidebar'], corner_radius=0,
                                width=220, border_width=0, border_color=C['divider'])
        sidebar.grid(row=0, column=0, sticky='nsew')
        sidebar.grid_propagate(False)

        # App title
        title_frame = ctk.CTkFrame(sidebar, fg_color='transparent')
        title_frame.pack(fill='x', padx=12, pady=(15, 5))
        ctk.CTkLabel(title_frame, text="GitHub Trending",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=C['text']).pack(anchor='w')
        ctk.CTkLabel(title_frame, text=f"Crawler {self._t('version')}",
                     font=F['caption'], text_color=C['text3']).pack(anchor='w')

        # Divider
        ctk.CTkFrame(sidebar, fg_color=C['divider'], height=1).pack(fill='x', padx=15, pady=12)

        # Nav items
        nav_items = [
            ('trending', self._t('trending'), '📊'),
            ('search', self._t('search'), '🔍'),
            ('url_dl', self._t('url_dl'), '🔗'),
            ('gh_dl', self._t('gh_dl'), '⬇️'),
            ('settings', self._t('settings'), '⚙️'),
        ]

        nav_frame = ctk.CTkFrame(sidebar, fg_color='transparent')
        nav_frame.pack(fill='x', padx=8)

        for key, text, icon in nav_items:
            btn = Win11NavButton(nav_frame, text, icon,
                                 command=lambda k=key: self._show_page(k))
            btn.pack(fill='x', pady=1)
            self.nav_buttons[key] = btn

        # Version at bottom
        ctk.CTkLabel(sidebar, text="v2.0.0", font=F['caption'],
                     text_color=C['text3']).pack(side='bottom', pady=10)

    def _show_page(self, name):
        for key, btn in self.nav_buttons.items():
            btn.set_active(key == name)
        self.pages[name].tkraise()

    # ==================== Helper ====================

    def _t(self, key, *args):
        val = LANG.get(self.lang, LANG['zh']).get(key, LANG['zh'].get(key, key))
        if args:
            return val.format(*args)
        return val

    def _make_tree(self, parent, columns, headings, widths):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Win11.Treeview', background=C['card'], foreground=C['text'],
                        fieldbackground=C['card'], rowheight=40, font=('Segoe UI Variable', 12),
                        borderwidth=0, relief='flat')
        style.configure('Win11.Treeview.Heading', background=C['card'], foreground=C['text2'],
                        font=('Segoe UI Variable', 12), borderwidth=0, relief='flat')
        style.map('Win11.Treeview',
                  background=[('selected', C['selected'])],
                  foreground=[('selected', C['text'])])
        style.map('Win11.Treeview.Heading', background=[('active', C['hover'])])

        frame = ctk.CTkFrame(parent, fg_color=C['card'], corner_radius=8,
                              border_width=1, border_color=C['border'])
        frame.pack(fill='both', expand=True, padx=12, pady=(0, 8))

        tree = ttk.Treeview(frame, columns=columns, show='headings', style='Win11.Treeview')
        for col, head, w in zip(columns, headings, widths):
            tree.heading(col, text=head)
            a = 'center' if col in ('index', 'language', 'action') else 'w'
            if col in ('stars', 'forks'):
                a = 'e'
            stretch = col in ('description', 'name')
            tree.column(col, width=w, anchor=a, minwidth=40, stretch=stretch)

        sb = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side='left', fill='both', expand=True, padx=(8, 0), pady=8)
        sb.pack(side='right', fill='y', padx=(0, 8), pady=8)
        return tree

    def _make_log(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=C['card'], corner_radius=8,
                              border_width=1, border_color=C['border'])
        frame.pack(fill='both', expand=True, padx=12, pady=(0, 12))
        box = ctk.CTkTextbox(frame, fg_color=C['card'], text_color=C['text'],
                              font=ctk.CTkFont(family='Consolas', size=11),
                              corner_radius=0, border_width=0)
        box.pack(fill='both', expand=True, padx=8, pady=8)
        box.configure(state='disabled')
        return box

    def _log(self, box, msg):
        try:
            box.configure(state='normal')
            box.insert('end', msg + '\n')
            box.see('end')
            box.configure(state='disabled')
        except Exception:
            pass

    def _section_label(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=F['heading'],
                     text_color=C['text']).pack(anchor='w', padx=16, pady=(12, 4))

    def _card(self, parent):
        f = ctk.CTkFrame(parent, fg_color=C['card'], corner_radius=8,
                          border_width=1, border_color=C['border'])
        f.pack(fill='x', padx=12, pady=(0, 8))
        return f

    # ==================== Trending Page ====================

    def _build_trending_page(self):
        p = self.pages['trending']

        self._section_label(p, self._t('trending'))

        card = self._card(p)
        row = ctk.CTkFrame(card, fg_color='transparent')
        row.pack(fill='x', padx=16, pady=12)

        ctk.CTkLabel(row, text=self._t('time'), font=F['body']).pack(side='left')
        self.trending_since = ctk.StringVar(value="weekly")
        for txt, val in [(self._t('daily'), "daily"), (self._t('weekly'), "weekly"), (self._t('monthly'), "monthly")]:
            ctk.CTkRadioButton(row, text=txt, variable=self.trending_since, value=val,
                               fg_color=C['accent'], hover_color=C['accent_hover'],
                               font=F['body']).pack(side='left', padx=10)

        ctk.CTkLabel(row, text=self._t('language'), font=F['body']).pack(side='left', padx=(20, 5))
        self.trending_lang = ctk.StringVar()
        ctk.CTkEntry(row, textvariable=self.trending_lang, width=100,
                     fg_color=C['card'], border_color=C['border']).pack(side='left', padx=5)

        ctk.CTkLabel(row, text=self._t('count'), font=F['body']).pack(side='left', padx=(15, 5))
        self.trending_limit = ctk.StringVar(value="20")
        ctk.CTkEntry(row, textvariable=self.trending_limit, width=50,
                     fg_color=C['card'], border_color=C['border']).pack(side='left', padx=5)

        ctk.CTkButton(row, text=self._t('fetch_trending'), command=self._fetch_trending,
                      fg_color=C['accent'], hover_color=C['accent_hover'],
                      font=F['body'], height=30, corner_radius=6).pack(side='left', padx=15)
        ctk.CTkButton(row, text="下载选中", command=self._dl_selected_trending,
                      fg_color=C['green'], hover_color=C['green_hover'],
                      font=F['body'], height=30, corner_radius=6).pack(side='left', padx=5)

        self.trending_tree = self._make_tree(
            p, ("sel", "name", "language", "stars", "forks", "description", "action"),
            ("☑", "仓库名称", "语言", "Stars", "Forks", "描述", "操作"),
            [35, 200, 70, 80, 80, 305, 60])
        self.trending_tree.bind("<ButtonRelease-1>", self._on_trending_click)

    def _on_trending_click(self, e):
        if self.trending_tree.identify_region(e.x, e.y) != "cell":
            return
        item = self.trending_tree.identify_row(e.y)
        if not item:
            return
        col = self.trending_tree.identify_column(e.x)
        vals = list(self.trending_tree.item(item)['values'])
        if col == '#1':
            vals[0] = '☐' if vals[0] == '☑' else '☑'
            self.trending_tree.item(item, values=vals)
            return
        name = vals[1]
        for r in self.current_repos:
            if r.get('name') == name:
                if col == "#7":
                    self._goto_dl([r])
                else:
                    self._open_detail(r)
                break

    # ==================== Search Page ====================

    def _build_search_page(self):
        p = self.pages['search']

        self._section_label(p, self._t('search'))

        card = self._card(p)
        row = ctk.CTkFrame(card, fg_color='transparent')
        row.pack(fill='x', padx=16, pady=12)

        ctk.CTkLabel(row, text=self._t('keyword'), font=F['body']).pack(side='left')
        self.search_query = ctk.StringVar()
        ctk.CTkEntry(row, textvariable=self.search_query, width=180,
                     fg_color=C['card'], border_color=C['border']).pack(side='left', padx=5)

        ctk.CTkLabel(row, text=self._t('language'), font=F['body']).pack(side='left', padx=(15, 5))
        self.search_lang = ctk.StringVar()
        ctk.CTkEntry(row, textvariable=self.search_lang, width=90,
                     fg_color=C['card'], border_color=C['border']).pack(side='left', padx=5)

        ctk.CTkLabel(row, text=self._t('count'), font=F['body']).pack(side='left', padx=(15, 5))
        self.search_limit = ctk.StringVar(value="20")
        ctk.CTkEntry(row, textvariable=self.search_limit, width=50,
                     fg_color=C['card'], border_color=C['border']).pack(side='left', padx=5)

        ctk.CTkButton(row, text=self._t('btn_search'), command=self._search_repos,
                      fg_color=C['accent'], hover_color=C['accent_hover'],
                      font=F['body'], height=30, corner_radius=6).pack(side='left', padx=15)
        ctk.CTkButton(row, text="下载选中", command=self._dl_selected_search,
                      fg_color=C['green'], hover_color=C['green_hover'],
                      font=F['body'], height=30, corner_radius=6).pack(side='left', padx=5)

        # Split view
        body = ctk.CTkFrame(p, fg_color='transparent')
        body.pack(fill='both', expand=True, padx=12, pady=(0, 8))
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self.search_tree = self._make_tree(
            body, ("sel", "name", "owner", "language", "stars", "forks", "action"),
            ("☑", "仓库名称", "作者", "语言", "Stars", "Forks", "操作"),
            [35, 170, 90, 60, 70, 70, 60])
        self.search_tree.pack_forget()
        self.search_tree.master.pack(side='left', fill='both', expand=True)

        self.search_tree.bind("<<TreeviewSelect>>", self._on_search_sel)
        self.search_tree.bind("<ButtonRelease-1>", self._on_search_click)

        # Detail panel
        right = ctk.CTkFrame(body, fg_color=C['card'], corner_radius=8, width=250,
                              border_width=1, border_color=C['border'])
        right.pack(side='right', fill='y', padx=(8, 0))
        right.pack_propagate(False)

        ctk.CTkLabel(right, text=self._t('repo_detail'), font=F['heading'],
                     text_color=C['text']).pack(anchor='w', padx=16, pady=(14, 8))

        self.detail = {}
        for key, label in [('name', '名称'), ('owner', '作者'), ('desc', '描述'),
                           ('lang', '语言'), ('stars', 'Stars'), ('forks', 'Forks'),
                           ('watchers', 'Watch'), ('issues', 'Issues'), ('license', 'License')]:
            lbl = ctk.CTkLabel(right, text=f"{label}: -", font=F['small'],
                               text_color=C['text2'], anchor='w', wraplength=220)
            lbl.pack(anchor='w', padx=16, pady=2)
            self.detail[key] = lbl

        ctk.CTkFrame(right, fg_color=C['divider'], height=1).pack(fill='x', padx=16, pady=10)

        self.detail_url = ctk.CTkLabel(right, text="", font=F['small'],
                                        text_color=C['accent'], cursor='hand2')
        self.detail_url.pack(anchor='w', padx=16, pady=3)
        self.detail_url.bind("<Button-1>", lambda e: self._open_url())

        ctk.CTkButton(right, text="下载此仓库", command=self._dl_selected_search,
                      fg_color=C['accent'], hover_color=C['accent_hover'],
                      font=F['body'], height=32, corner_radius=6).pack(fill='x', padx=16, pady=(10, 14))

    def _on_search_sel(self, e):
        sel = self.search_tree.selection()
        if not sel:
            return
        name = self.search_tree.item(sel[0])['values'][1]
        for r in self.current_repos:
            if r.get('name') == name:
                self._update_detail(r)
                break

    def _on_search_click(self, e):
        if self.search_tree.identify_region(e.x, e.y) != "cell":
            return
        item = self.search_tree.identify_row(e.y)
        if not item:
            return
        col = self.search_tree.identify_column(e.x)
        vals = list(self.search_tree.item(item)['values'])
        if col == '#1':
            vals[0] = '☐' if vals[0] == '☑' else '☑'
            self.search_tree.item(item, values=vals)
            return
        name = vals[1]
        for r in self.current_repos:
            if r.get('name') == name:
                if col == "#7":
                    self._goto_dl([r])
                else:
                    self._open_detail(r)
                break

    def _update_detail(self, r):
        self.detail['name'].configure(text=f"名称: {r.get('name', '-')}")
        self.detail['owner'].configure(text=f"作者: {r.get('owner', '-')}")
        desc = r.get('description', '-')
        if len(desc) > 70:
            desc = desc[:70] + "..."
        self.detail['desc'].configure(text=f"描述: {desc}")
        self.detail['lang'].configure(text=f"语言: {r.get('language', '-')}")
        self.detail['stars'].configure(text=f"Stars: {r.get('stars', 0):,}")
        self.detail['forks'].configure(text=f"Forks: {r.get('forks', 0):,}")
        self.detail['watchers'].configure(text=f"Watch: {r.get('watchers', 0):,}")
        self.detail['issues'].configure(text=f"Issues: {r.get('open_issues', 0):,}")
        lic = r.get('license', '-')
        if isinstance(lic, dict):
            lic = lic.get('name', '-')
        self.detail['license'].configure(text=f"License: {lic or '-'}")
        self.current_repo_url = r.get('url', '')
        self.detail_url.configure(text=self.current_repo_url if self.current_repo_url else "")

    def _open_url(self):
        if self.current_repo_url:
            import webbrowser
            webbrowser.open(self.current_repo_url)

    def _get_checked_repos(self, tree):
        """获取 Treeview 中所有勾选的仓库。"""
        checked = []
        for item in tree.get_children():
            vals = tree.item(item)['values']
            if vals and vals[0] == '☑':
                name = vals[1]
                for r in self.current_repos:
                    if r.get('name') == name:
                        checked.append(r)
                        break
        return checked

    def _dl_selected_trending(self):
        repos = self._get_checked_repos(self.trending_tree)
        if repos:
            self._goto_dl(repos)
        else:
            messagebox.showinfo(self._t('hint'), "请先勾选要下载的仓库")

    def _dl_selected_search(self):
        repos = self._get_checked_repos(self.search_tree)
        if repos:
            self._goto_dl(repos)
        else:
            messagebox.showinfo(self._t('hint'), "请先勾选要下载的仓库")

    # ==================== URL Download Page ====================

    def _build_url_page(self):
        p = self.pages['url_dl']
        self._section_label(p, self._t('url_dl'))

        card = self._card(p)
        inner = ctk.CTkFrame(card, fg_color='transparent')
        inner.pack(fill='x', padx=16, pady=12)

        ctk.CTkLabel(inner, text=f"{self._t('url_dl')}:", font=F['body']).pack(anchor='w')
        self.url_input = ctk.StringVar()
        ctk.CTkEntry(inner, textvariable=self.url_input, fg_color=C['card'],
                     border_color=C['border'], height=32).pack(fill='x', pady=(4, 8))

        btn_row = ctk.CTkFrame(inner, fg_color='transparent')
        btn_row.pack(fill='x', pady=4)
        ctk.CTkButton(btn_row, text=self._t('single_dl'), command=self._dl_single_url,
                      fg_color=C['accent'], hover_color=C['accent_hover'],
                      height=30, corner_radius=6, font=F['body']).pack(side='left', padx=(0, 6))
        ctk.CTkButton(btn_row, text=self._t('batch_dl'), command=self._show_batch,
                      fg_color=C['accent'], hover_color=C['accent_hover'],
                      height=30, corner_radius=6, font=F['body']).pack(side='left', padx=6)
        ctk.CTkButton(btn_row, text=self._t('choose_dir'), command=self._browse_url_dir,
                      fg_color=C['hover'], hover_color=C['border'],
                      height=30, corner_radius=6, font=F['body'],
                      text_color=C['text']).pack(side='left', padx=6)

        dir_row = ctk.CTkFrame(inner, fg_color='transparent')
        dir_row.pack(fill='x', pady=4)
        ctk.CTkLabel(dir_row, text=self._t('save_location'), font=F['body']).pack(side='left')
        self.url_download_dir = ctk.StringVar(value=self.config.get_download_dir())
        ctk.CTkEntry(dir_row, textvariable=self.url_download_dir,
                     fg_color=C['card'], border_color=C['border']).pack(side='left', fill='x', expand=True, padx=8)

        opt_row = ctk.CTkFrame(inner, fg_color='transparent')
        opt_row.pack(fill='x', pady=(4, 0))
        ctk.CTkLabel(opt_row, text=self._t('threads'), font=F['body']).pack(side='left')
        self.url_workers = ctk.StringVar(value="5")
        ctk.CTkOptionMenu(opt_row, variable=self.url_workers, values=[str(i) for i in range(1, 21)],
                          fg_color=C['card'], button_color=C['accent'], text_color=C['text'], width=60).pack(side='left', padx=8)
        ctk.CTkLabel(opt_row, text=self._t('timeout'), font=F['body']).pack(side='left', padx=(10, 0))
        self.url_timeout = ctk.StringVar(value="60")
        ctk.CTkOptionMenu(opt_row, variable=self.url_timeout, values=["30", "60", "120", "300"],
                          fg_color=C['card'], button_color=C['accent'], text_color=C['text'], width=70).pack(side='left', padx=8)

        # Progress
        prog_card = self._card(p)
        prog_top = ctk.CTkFrame(prog_card, fg_color='transparent')
        prog_top.pack(fill='x', padx=16, pady=(10, 3))
        ctk.CTkLabel(prog_top, text=self._t('download_progress'), font=F['body'],
                     text_color=C['text2']).pack(side='left')
        self.url_stop_btn = ctk.CTkButton(prog_top, text=self._t('stop'), command=self._stop_url_dl,
                                          fg_color=C['red'], hover_color=C['red_hover'],
                                          width=55, height=24, corner_radius=6,
                                          font=F['small'], state='disabled')
        self.url_stop_btn.pack(side='right')
        self.url_progress = ctk.CTkProgressBar(prog_card, fg_color=C['border'],
                                                progress_color=C['accent'], height=6, corner_radius=3)
        self.url_progress.pack(fill='x', padx=16, pady=3)
        self.url_progress.set(0)
        self.url_progress_label = ctk.CTkLabel(prog_card, text=self._t('ready'), font=F['caption'],
                                                text_color=C['text3'])
        self.url_progress_label.pack(anchor='w', padx=16, pady=(0, 10))
        self.url_download_cancel = False

        self.url_log = self._make_log(p)

    def _browse_url_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.url_download_dir.set(d)

    def _stop_url_dl(self):
        self.url_download_cancel = True
        self._url_log("用户终止...")
        self.url_stop_btn.configure(state='disabled')

    def _dl_single_url(self):
        url = self.url_input.get().strip()
        if url:
            self._do_url_dl(url)

    def _show_batch(self):
        dlg = ctk.CTkToplevel(self)
        dlg.title("批量下载")
        dlg.geometry("550x380")
        dlg.configure(fg_color=C['bg'])
        dlg.transient(self)
        dlg.grab_set()

        ctk.CTkLabel(dlg, text=self._t('batch_hint'), font=F['body']).pack(padx=15, pady=10)
        box = ctk.CTkTextbox(dlg, fg_color=C['card'], text_color=C['text'],
                              font=ctk.CTkFont(family='Consolas', size=11))
        box.pack(fill='both', expand=True, padx=15, pady=5)

        def go():
            urls = [u.strip() for u in box.get('1.0', 'end').strip().split('\n') if u.strip()]
            if urls:
                dlg.destroy()
                self._batch_dl(urls)

        ctk.CTkButton(dlg, text=self._t('start_download'), command=go,
                      fg_color=C['accent'], hover_color=C['accent_hover'],
                      height=32, corner_radius=6).pack(pady=10)

    def _extract_filename(self, resp, url):
        """从 Content-Disposition / URL 查询参数 / URL 路径提取文件名。"""
        import re as _re
        from urllib.parse import parse_qs
        # 1. 从响应头 Content-Disposition 获取
        cd = resp.headers.get('content-disposition', '')
        if cd:
            m = _re.search(r"filename\*=UTF-8''(.+?)(?:;|$)", cd, _re.IGNORECASE)
            if m:
                return unquote(m.group(1).strip())
            m = _re.search(r'filename="?([^";]+)"?', cd, _re.IGNORECASE)
            if m:
                return unquote(m.group(1).strip())
        # 2. 从 URL 查询参数获取 (GitHub release assets 等)
        qs = parse_qs(urlparse(url).query)
        for key in ['response-content-disposition', 'rscd']:
            val = qs.get(key, [''])[0]
            if val:
                m = _re.search(r'filename="?([^";]+)"?', val, _re.IGNORECASE)
                if m:
                    return unquote(m.group(1).strip())
        # 3. 从 URL 路径获取
        name = os.path.basename(urlparse(url).path)
        if name and '.' in name:
            return unquote(name)
        # 4. 从重定向后的 URL 获取
        final_url = resp.url
        if final_url != url:
            qs2 = parse_qs(urlparse(final_url).query)
            for key in ['response-content-disposition', 'rscd']:
                val = qs2.get(key, [''])[0]
                if val:
                    m = _re.search(r'filename="?([^";]+)"?', val, _re.IGNORECASE)
                    if m:
                        return unquote(m.group(1).strip())
            name = os.path.basename(urlparse(final_url).path)
            if name and '.' in name:
                return unquote(name)
        return None

    def _do_url_dl(self, url, fn=None):
        def _run():
            try:
                self.url_download_cancel = False
                self.after(0, lambda: self.url_stop_btn.configure(state='normal'))
                out = self.url_download_dir.get()
                timeout = int(self.url_timeout.get())
                os.makedirs(out, exist_ok=True)
                self._url_log(f"下载: {url}")
                self.url_progress_label.configure(text="获取文件信息...")
                resp = requests.get(url, stream=True, timeout=timeout)
                resp.raise_for_status()
                if not fn:
                    name = self._extract_filename(resp, url) or "download"
                    save = os.path.join(out, name)
                else:
                    save = os.path.join(out, fn)
                total = int(resp.headers.get('content-length', 0))
                dl = 0
                with open(save, 'wb') as f:
                    for c in resp.iter_content(65536):
                        if self.url_download_cancel:
                            resp.close()
                            f.close()
                            if os.path.exists(save):
                                os.remove(save)
                            self.after(0, lambda: self.url_progress.set(0))
                            self.after(0, lambda: self.url_progress_label.configure(text=self._t('stopped')))
                            self._url_log("已终止")
                            self.after(0, lambda: self.url_stop_btn.configure(state='disabled'))
                            return
                        if c:
                            f.write(c)
                            dl += len(c)
                            if total > 0:
                                pct = dl / total
                                self.after(0, lambda p=pct, d=dl, t=total: (
                                    self.url_progress.set(p),
                                    self.url_progress_label.configure(
                                        text=f"{d/(1024*1024):.2f}/{t/(1024*1024):.2f} MB ({p*100:.1f}%)")))
                sz = os.path.getsize(save)
                self.after(0, lambda: self.url_progress.set(1))
                self.after(0, lambda s=sz: self.url_progress_label.configure(text=f"完成 {s/(1024*1024):.2f} MB"))
                self._url_log(f"完成 {sz/(1024*1024):.2f} MB")
                self.after(0, lambda: self.url_stop_btn.configure(state='disabled'))
            except Exception as e:
                self._url_log(f"失败: {e}")
                self.after(0, lambda: self.url_progress_label.configure(text=self._t('failed')))
                self.after(0, lambda: self.url_stop_btn.configure(state='disabled'))
        threading.Thread(target=_run, daemon=True).start()

    def _batch_dl(self, urls):
        def _run():
            self.url_download_cancel = False
            self.after(0, lambda: self.url_stop_btn.configure(state='normal'))
            w = int(self.url_workers.get())
            t = len(urls)
            done, fail = [0], [0]
            self._url_log(f"批量 {t} 个文件, {w} 线程")
            def dl_one(u):
                if self.url_download_cancel:
                    return
                try:
                    out = self.url_download_dir.get()
                    os.makedirs(out, exist_ok=True)
                    r = requests.get(u, stream=True, timeout=int(self.url_timeout.get()))
                    r.raise_for_status()
                    name = self._extract_filename(r, u) or f"file_{done[0]}"
                    save = os.path.join(out, name)
                    with open(save, 'wb') as f:
                        for c in r.iter_content(8192):
                            if self.url_download_cancel:
                                r.close(); f.close()
                                if os.path.exists(save): os.remove(save)
                                return
                            if c: f.write(c)
                    done[0] += 1
                    self._url_log(f"完成: {name}")
                    self.after(0, lambda d=done[0]: (
                        self.url_progress.set(d/t),
                        self.url_progress_label.configure(text=f"{d}/{t}")))
                except Exception as e:
                    fail[0] += 1
                    self._url_log(f"失败: {u} - {e}")
            with ThreadPoolExecutor(max_workers=w) as ex:
                list(as_completed(ex.submit(dl_one, u) for u in urls))
            if self.url_download_cancel:
                self._url_log(f"已终止 完成:{done[0]} 失败:{fail[0]}")
                self.after(0, lambda: self.url_progress_label.configure(text=self._t('stopped')))
            else:
                self._url_log(f"完成: 成功{done[0]} 失败{fail[0]}")
                self.after(0, lambda: self.url_progress_label.configure(
                    text=f"{self._t('completed')} {done[0]} {self._t('failed')} {fail[0]}"))
            self.after(0, lambda: self.url_stop_btn.configure(state='disabled'))
        threading.Thread(target=_run, daemon=True).start()

    def _url_log(self, msg):
        self._log(self.url_log, msg)

    # ==================== GitHub Download Page ====================

    def _build_gh_page(self):
        p = self.pages['gh_dl']
        self._section_label(p, self._t('gh_dl_title'))

        card = self._card(p)
        inner = ctk.CTkFrame(card, fg_color='transparent')
        inner.pack(fill='x', padx=16, pady=12)

        dir_row = ctk.CTkFrame(inner, fg_color='transparent')
        dir_row.pack(fill='x', pady=4)
        ctk.CTkLabel(dir_row, text=f"{self._t('download_dir')}:", font=F['body']).pack(side='left')
        self.github_download_dir = ctk.StringVar(value=self.config.get_download_dir())
        ctk.CTkEntry(dir_row, textvariable=self.github_download_dir,
                     fg_color=C['card'], border_color=C['border']).pack(side='left', fill='x', expand=True, padx=8)
        ctk.CTkButton(dir_row, text=self._t('browse'), command=self._browse_gh_dir,
                      fg_color=C['hover'], hover_color=C['border'],
                      width=55, height=28, corner_radius=6, font=F['small'],
                      text_color=C['text']).pack(side='left')

        opt_row = ctk.CTkFrame(inner, fg_color='transparent')
        opt_row.pack(fill='x', pady=4)
        ctk.CTkLabel(opt_row, text=self._t('concurrency'), font=F['body']).pack(side='left')
        self.github_workers = ctk.StringVar(value="5")
        ctk.CTkOptionMenu(opt_row, variable=self.github_workers, values=[str(i) for i in range(1, 11)],
                          fg_color=C['card'], button_color=C['accent'], text_color=C['text'], width=60).pack(side='left', padx=8)

        btn_row = ctk.CTkFrame(inner, fg_color='transparent')
        btn_row.pack(fill='x', pady=(8, 0))
        ctk.CTkButton(btn_row, text=self._t('dl_trending'), command=self._dl_trending,
                      fg_color=C['accent'], hover_color=C['accent_hover'],
                      height=30, corner_radius=6, font=F['body']).pack(side='left', padx=(0, 6))
        ctk.CTkButton(btn_row, text=self._t('dl_search'), command=self._dl_search,
                      fg_color=C['accent'], hover_color=C['accent_hover'],
                      height=30, corner_radius=6, font=F['body']).pack(side='left', padx=6)
        ctk.CTkButton(btn_row, text=self._t('dl_json'), command=self._dl_json,
                      fg_color=C['hover'], hover_color=C['border'],
                      height=30, corner_radius=6, font=F['body'],
                      text_color=C['text']).pack(side='left', padx=6)

        # Progress
        prog_card = self._card(p)
        top = ctk.CTkFrame(prog_card, fg_color='transparent')
        top.pack(fill='x', padx=16, pady=(10, 3))
        ctk.CTkLabel(top, text=self._t('download_progress'), font=F['body'], text_color=C['text2']).pack(side='left')
        self.github_stop_btn = ctk.CTkButton(top, text=self._t('stop'), command=self._stop_dl,
                                              fg_color=C['red'], hover_color=C['red_hover'],
                                              width=55, height=24, corner_radius=6,
                                              font=F['small'], state='disabled')
        self.github_stop_btn.pack(side='right')

        self.github_progress = ctk.CTkProgressBar(prog_card, fg_color=C['border'],
                                                   progress_color=C['green'], height=6, corner_radius=3)
        self.github_progress.pack(fill='x', padx=16, pady=3)
        self.github_progress.set(0)
        self.github_progress_label = ctk.CTkLabel(prog_card, text=self._t('ready'), font=F['caption'],
                                                   text_color=C['text3'])
        self.github_progress_label.pack(anchor='w', padx=16, pady=(0, 10))

        self.github_log = self._make_log(p)

    def _browse_gh_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.github_download_dir.set(d)

    def _dl_trending(self):
        if self.current_repos:
            self._do_gh_dl(self.current_repos)
        else:
            messagebox.showwarning("提示", "请先获取热榜")

    def _dl_search(self):
        if self.current_repos:
            self._do_gh_dl(self.current_repos)
        else:
            messagebox.showwarning("提示", "请先搜索")

    def _dl_json(self):
        fp = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if fp:
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    self._do_gh_dl(json.load(f))
            except Exception as e:
                messagebox.showerror("错误", str(e))

    def _goto_dl(self, repos):
        self._show_page('gh_dl')
        self._do_gh_dl(repos)

    def _do_gh_dl(self, repos):
        def _run():
            try:
                out = self.github_download_dir.get()
                workers = int(self.github_workers.get())
                self.is_downloading = True
                self.download_cancel = False
                self.github_stop_btn.configure(state='normal')

                self._gh_log(f"{'='*45}")
                self._gh_log(f"下载 {len(repos)} 个仓库 | 目录: {out}")
                self._gh_log(f"{'='*45}")
                self.github_progress.set(0)
                self.github_progress_label.configure(text="下载中...")
                os.makedirs(out, exist_ok=True)

                ok, fail = [0], [0]
                total = len(repos)
                import time as _t
                _ui_lock = threading.Lock()
                last = [0.0]

                def upd(idx, dl, ts, name):
                    now = _t.time()
                    with _ui_lock:
                        if now - last[0] < 0.15:
                            return
                        last[0] = now
                    mb = dl/(1024*1024)
                    if ts > 0:
                        pct = min(dl/ts, 1.0)
                        ov = min((idx+pct)/total, 0.999)
                        txt = f"[{idx+1}/{total}] {name} {mb:.1f}/{ts/(1024*1024):.1f} MB ({pct*100:.0f}%)"
                    else:
                        ov = min((idx+0.5)/total, 0.999)
                        txt = f"[{idx+1}/{total}] {name} {mb:.1f} MB"
                    def _u():
                        self.github_progress.set(ov)
                        self.github_progress_label.configure(text=txt)
                    self.after(0, _u)

                def dl_one(args):
                    idx, repo = args
                    if self.download_cancel:
                        return
                    name = repo.get('name', '?')
                    url = repo.get('url', '')
                    try:
                        parts = urlparse(url).path.strip('/').split('/')
                        if len(parts) < 2:
                            raise Exception("无效URL")
                        owner, rname = parts[0], parts[1].replace('.git', '')
                        for branch in ['main', 'master']:
                            zurl = f"https://github.com/{owner}/{rname}/archive/refs/heads/{branch}.zip"
                            self._gh_log(f"下载: {name} ({branch})")
                            # 先用 HEAD 请求获取真实文件大小
                            real_ts = 0
                            try:
                                h = requests.head(zurl, timeout=10, allow_redirects=True)
                                real_ts = int(h.headers.get('content-length', 0))
                            except Exception:
                                pass
                            sources = [f"https://ghfast.top/{zurl}", f"https://ghproxy.cn/{zurl}", zurl]
                            got = False
                            for si, su in enumerate(sources):
                                if got: break
                                sn = ["镜像1","镜像2","直连"][si]
                                try:
                                    self._gh_log(f"  {sn}...")
                                    resp = requests.get(su, timeout=(10,120), stream=True)
                                    if resp.status_code != 200:
                                        resp.close()
                                        continue
                                    ts = int(resp.headers.get('content-length', 0)) or real_ts
                                    if ts > 0:
                                        self._gh_log(f"  {ts/(1024*1024):.1f} MB")
                                    safe = name.replace('/', '_')
                                    save = os.path.join(out, f"{safe}.zip")
                                    dl = 0
                                    with open(save, 'wb') as f:
                                        for c in resp.iter_content(32768):
                                            if self.download_cancel:
                                                resp.close(); f.close()
                                                if os.path.exists(save): os.remove(save)
                                                return
                                            if c:
                                                f.write(c); dl += len(c)
                                                upd(idx, dl, ts, name)
                                    resp.close()
                                    if os.path.getsize(save) == 0:
                                        os.remove(save); continue
                                    got = True
                                    ok[0] += 1
                                    self._gh_log(f"  完成 {os.path.getsize(save)/(1024*1024):.1f} MB [{sn}]")
                                    break
                                except Exception as e:
                                    self._gh_log(f"  {sn}: {str(e)[:35]}")
                            if not got:
                                raise Exception("所有源失败")
                            upd(idx, ts or dl, ts or real_ts, name)
                            break
                    except Exception as e:
                        fail[0] += 1
                        self._gh_log(f"  失败: {name} - {str(e)[:45]}")

                with ThreadPoolExecutor(max_workers=workers) as ex:
                    list(as_completed(ex.submit(dl_one, (i,r)) for i,r in enumerate(repos)))

                self.is_downloading = False
                self.github_stop_btn.configure(state='disabled')
                if self.download_cancel:
                    self.github_progress.set(0)
                    self.github_progress_label.configure(text="已终止")
                    self._gh_log(f"已终止 完成:{ok[0]} 失败:{fail[0]}")
                else:
                    self.github_progress.set(1)
                    self.github_progress_label.configure(text=f"完成 成功:{ok[0]} 失败:{fail[0]}")
                    self._gh_log(f"完成 成功:{ok[0]} 失败:{fail[0]}")
                    self.after(0, lambda: messagebox.showinfo("完成", f"成功:{ok[0]}\n失败:{fail[0]}"))
            except Exception as e:
                self.is_downloading = False
                self.github_stop_btn.configure(state='disabled')
                self._gh_log(f"错误: {e}")
        threading.Thread(target=_run, daemon=True).start()

    def _stop_dl(self):
        if self.is_downloading:
            self.download_cancel = True
            self._gh_log("用户终止...")
            self.github_stop_btn.configure(state='disabled')

    def _gh_log(self, msg):
        self._log(self.github_log, msg)

    # ==================== Detail Page ====================

    def _open_detail(self, repo):
        dlg = ctk.CTkToplevel(self)
        dlg.title(repo.get('name', 'Detail'))
        dlg.geometry("800x700")
        dlg.configure(fg_color=C['bg'])
        dlg.transient(self)
        dlg.after(100, dlg.grab_set)

        # --- Info card ---
        info = ctk.CTkFrame(dlg, fg_color=C['card'], corner_radius=8,
                             border_width=1, border_color=C['border'])
        info.pack(fill='x', padx=12, pady=(12, 6))

        ctk.CTkLabel(info, text=repo.get('name', ''), font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=C['text']).pack(anchor='w', padx=16, pady=(12, 2))
        owner = repo.get('owner', '')
        if isinstance(owner, dict):
            owner = owner.get('login', '')
        ctk.CTkLabel(info, text=f"{self._t('author')}: {owner}", font=F['body'],
                     text_color=C['text2']).pack(anchor='w', padx=16)
        desc = repo.get('description', '') or ''
        ctk.CTkLabel(info, text=desc, font=F['body'], text_color=C['text'],
                     wraplength=750, justify='left').pack(anchor='w', padx=16, pady=(4, 6))

        stats = ctk.CTkFrame(info, fg_color='transparent')
        stats.pack(fill='x', padx=16, pady=(0, 10))
        for label, val in [
            (self._t('stars'), f"{repo.get('stars', 0):,}"),
            (self._t('forks'), f"{repo.get('forks', 0):,}"),
            (self._t('watchers'), f"{repo.get('watchers', 0):,}"),
            (self._t('issues'), f"{repo.get('open_issues', 0):,}"),
            (self._t('language'), repo.get('language', '-')),
        ]:
            f = ctk.CTkFrame(stats, fg_color=C['accent_light'], corner_radius=6)
            f.pack(side='left', padx=(0, 8))
            ctk.CTkLabel(f, text=f"{label}: {val}", font=F['small'],
                         text_color=C['accent']).pack(padx=10, pady=4)

        topics = repo.get('topics', [])
        if topics:
            tf = ctk.CTkFrame(info, fg_color='transparent')
            tf.pack(fill='x', padx=16, pady=(0, 8))
            ctk.CTkLabel(tf, text=f"{self._t('topics')}:", font=F['small'],
                         text_color=C['text2']).pack(side='left')
            for t in topics[:8]:
                ctk.CTkLabel(tf, text=t, font=F['caption'], fg_color=C['accent_light'],
                             text_color=C['accent'], corner_radius=4).pack(side='left', padx=3)

        btn_row = ctk.CTkFrame(info, fg_color='transparent')
        btn_row.pack(fill='x', padx=16, pady=(0, 12))
        url = repo.get('url', '')
        ctk.CTkButton(btn_row, text=self._t('open_github'),
                      command=lambda: self._open_url2(url),
                      fg_color=C['accent'], hover_color=C['accent_hover'],
                      font=F['body'], height=30, corner_radius=6).pack(side='left', padx=(0, 8))
        ctk.CTkButton(btn_row, text=self._t('download_repo'),
                      command=lambda: self._goto_dl([repo]),
                      fg_color=C['green'], hover_color=C['green_hover'],
                      font=F['body'], height=30, corner_radius=6).pack(side='left')

        # --- README ---
        readme_frame = ctk.CTkFrame(dlg, fg_color=C['card'], corner_radius=8,
                                     border_width=1, border_color=C['border'])
        readme_frame.pack(fill='both', expand=True, padx=12, pady=6)

        readme_top = ctk.CTkFrame(readme_frame, fg_color='transparent')
        readme_top.pack(fill='x', padx=12, pady=(8, 4))
        ctk.CTkLabel(readme_top, text=self._t('readme'), font=F['heading'],
                     text_color=C['text']).pack(side='left')

        readme_text = ctk.CTkTextbox(readme_frame, fg_color=C['card'], text_color=C['text'],
                                      font=ctk.CTkFont(family='Consolas', size=12),
                                      corner_radius=0, border_width=0)
        readme_text.pack(fill='both', expand=True, padx=12, pady=(0, 8))
        readme_text.configure(state='disabled')

        readme_original = ['']
        btn_frame = ctk.CTkFrame(readme_top, fg_color='transparent')
        btn_frame.pack(side='right')

        def set_readme(text):
            readme_text.configure(state='normal')
            readme_text.delete('1.0', 'end')
            readme_text.insert('1.0', text)
            readme_text.configure(state='disabled')

        def load_readme():
            def _run():
                try:
                    name = repo.get('name', '')
                    if not name:
                        return
                    headers = {"Accept": "application/vnd.github.v3.raw"}
                    if self.crawler.token:
                        headers["Authorization"] = f"token {self.crawler.token}"
                    r = requests.get(f"https://api.github.com/repos/{name}/readme",
                                     headers=headers, timeout=15)
                    if r.status_code == 200:
                        content = r.text
                        readme_original[0] = content
                        dlg.after(0, lambda: set_readme(content))
                    else:
                        dlg.after(0, lambda: set_readme(f"[README 加载失败: HTTP {r.status_code}]"))
                except Exception as e:
                    dlg.after(0, lambda: set_readme(f"[README 加载失败: {e}]"))
            threading.Thread(target=_run, daemon=True).start()

        def translate_readme(direction):
            if not readme_original[0]:
                return
            src = readme_original[0][:3000]
            def _run():
                try:
                    dlg.after(0, lambda: set_readme(self._t('translating')))
                    result = self._translate_text(src, direction)
                    dlg.after(0, lambda: set_readme(result))
                except Exception as e:
                    dlg.after(0, lambda: set_readme(f"{self._t('translate_failed')}: {e}"))
            threading.Thread(target=_run, daemon=True).start()

        ctk.CTkButton(btn_frame, text=self._t('translate_zh_en'), width=60, height=24,
                      font=F['caption'], fg_color=C['hover'], text_color=C['text'],
                      hover_color=C['border'], corner_radius=4,
                      command=lambda: translate_readme('zh_en')).pack(side='left', padx=2)
        ctk.CTkButton(btn_frame, text=self._t('translate_en_zh'), width=60, height=24,
                      font=F['caption'], fg_color=C['hover'], text_color=C['text'],
                      hover_color=C['border'], corner_radius=4,
                      command=lambda: translate_readme('en_zh')).pack(side='left', padx=2)
        ctk.CTkButton(btn_frame, text=self._t('show_original'), width=70, height=24,
                      font=F['caption'], fg_color=C['hover'], text_color=C['text'],
                      hover_color=C['border'], corner_radius=4,
                      command=lambda: set_readme(readme_original[0]) if readme_original[0] else None).pack(side='left', padx=2)

        # --- Issues ---
        issues_frame = ctk.CTkFrame(dlg, fg_color=C['card'], corner_radius=8,
                                     border_width=1, border_color=C['border'])
        issues_frame.pack(fill='x', padx=12, pady=(6, 12))

        iss_top = ctk.CTkFrame(issues_frame, fg_color='transparent')
        iss_top.pack(fill='x', padx=12, pady=(8, 4))
        ctk.CTkLabel(iss_top, text=self._t('open_issues'), font=F['heading'],
                     text_color=C['text']).pack(side='left')
        iss_count = repo.get('open_issues', 0)
        ctk.CTkLabel(iss_top, text=f"({iss_count})", font=F['body'],
                     text_color=C['text2']).pack(side='left', padx=6)

        issues_box = ctk.CTkScrollableFrame(issues_frame, fg_color=C['card'], height=200)
        issues_box.pack(fill='x', padx=12, pady=(0, 8))

        def load_issues():
            for w in issues_box.winfo_children():
                w.destroy()
            ctk.CTkLabel(issues_box, text=self._t('loading'),
                         font=F['body'], text_color=C['text3']).pack(pady=10)
            def _run():
                try:
                    name = repo.get('name', '')
                    headers = {}
                    if self.crawler.token:
                        headers["Authorization"] = f"token {self.crawler.token}"
                    r = requests.get(f"https://api.github.com/repos/{name}/issues",
                                     params={"state": "open", "per_page": 10, "sort": "updated"},
                                     headers=headers, timeout=15)
                    if r.status_code != 200:
                        dlg.after(0, lambda: self._fill_issues_error(issues_box, r.status_code))
                        return
                    items = r.json()
                    dlg.after(0, lambda: self._fill_issues(issues_box, items, name, headers))
                except Exception as e:
                    dlg.after(0, lambda: self._fill_issues_error(issues_box, str(e)))
            threading.Thread(target=_run, daemon=True).start()

        ctk.CTkButton(iss_top, text=self._t('load_issues'), width=80, height=24,
                      font=F['caption'], fg_color=C['accent'], hover_color=C['accent_hover'],
                      corner_radius=4, command=load_issues).pack(side='right')

        # Auto-load
        load_readme()
        if iss_count > 0:
            load_issues()

    def _fill_issues(self, box, items, repo_name, headers):
        for w in box.winfo_children():
            w.destroy()
        if not items:
            ctk.CTkLabel(box, text=self._t('no_issues'),
                         font=F['body'], text_color=C['text3']).pack(pady=10)
            return
        for iss in items:
            row = ctk.CTkFrame(box, fg_color=C['bg'], corner_radius=6)
            row.pack(fill='x', pady=2)
            title = iss.get('title', '')
            user = iss.get('user', {}).get('login', '')
            labels = ', '.join(l.get('name', '') for l in iss.get('labels', []))
            time_str = iss.get('created_at', '')[:10]
            num = iss.get('number', 0)

            header_text = f"#{num} {title}"
            ctk.CTkLabel(row, text=header_text, font=F['body'], text_color=C['accent'],
                         anchor='w', wraplength=700, justify='left').pack(fill='x', padx=10, pady=(6, 0))
            meta = f"{self._t('by')} {user}  |  {time_str}"
            if labels:
                meta += f"  |  {labels}"
            ctk.CTkLabel(row, text=meta, font=F['caption'], text_color=C['text3'],
                         anchor='w').pack(fill='x', padx=10, pady=(0, 2))

            body_text = iss.get('body', '') or ''
            if body_text:
                body_preview = body_text[:200].replace('\n', ' ')
                if len(body_text) > 200:
                    body_preview += '...'
                ctk.CTkLabel(row, text=body_preview, font=F['small'], text_color=C['text2'],
                             anchor='w', wraplength=700, justify='left').pack(fill='x', padx=10, pady=(0, 4))

                def make_expand(n=num, r=repo_name, h=headers, parent=row):
                    self._load_issue_comments(parent, r, n, h)

                ctk.CTkLabel(row, text=self._t('click_to_expand'), font=F['caption'],
                             text_color=C['text3'], cursor='hand2', anchor='w').pack(anchor='w', padx=10, pady=(0, 6))
                row.bind('<Button-1>', lambda e, fn=make_expand: fn())
                for child in row.winfo_children():
                    child.bind('<Button-1>', lambda e, fn=make_expand: fn())

    def _fill_issues_error(self, box, err):
        for w in box.winfo_children():
            w.destroy()
        ctk.CTkLabel(box, text=f"加载失败: {err}", font=F['body'],
                     text_color=C['red']).pack(pady=10)

    def _load_issue_comments(self, parent, repo_name, issue_num, headers):
        detail_win = ctk.CTkToplevel(self)
        detail_win.title(f"#{issue_num}")
        detail_win.geometry("700x500")
        detail_win.configure(fg_color=C['bg'])
        detail_win.transient(self)
        detail_win.after(100, detail_win.grab_set)

        scroll = ctk.CTkScrollableFrame(detail_win, fg_color=C['bg'])
        scroll.pack(fill='both', expand=True, padx=12, pady=12)

        ctk.CTkLabel(scroll, text=self._t('loading'), font=F['body'],
                     text_color=C['text3']).pack(pady=10)

        def _run():
            try:
                r = requests.get(f"https://api.github.com/repos/{repo_name}/issues/{issue_num}",
                                 headers=headers, timeout=15)
                cr = requests.get(f"https://api.github.com/repos/{repo_name}/issues/{issue_num}/comments",
                                  headers=headers, timeout=15)
                issue = r.json() if r.status_code == 200 else {}
                comments = cr.json() if cr.status_code == 200 else []
                detail_win.after(0, lambda: self._render_issue_detail(scroll, issue, comments))
            except Exception as e:
                detail_win.after(0, lambda: ctk.CTkLabel(scroll, text=f"Error: {e}",
                                                         font=F['body'], text_color=C['red']).pack(pady=10))
        threading.Thread(target=_run, daemon=True).start()

    def _render_issue_detail(self, scroll, issue, comments):
        for w in scroll.winfo_children():
            w.destroy()
        if not issue:
            ctk.CTkLabel(scroll, text="加载失败", font=F['body'], text_color=C['red']).pack(pady=10)
            return
        # Issue body
        ctk.CTkLabel(scroll, text=f"#{issue.get('number','')} {issue.get('title','')}",
                     font=F['heading'], text_color=C['text'], anchor='w',
                     wraplength=650, justify='left').pack(fill='x', pady=(0, 6))
        body = issue.get('body', '') or '(无内容)'
        ctk.CTkTextbox(scroll, fg_color=C['card'], text_color=C['text'],
                        font=ctk.CTkFont(family='Consolas', size=12),
                        corner_radius=6, border_width=1, border_color=C['border']).pack(fill='x', pady=4)
        tb = scroll.winfo_children()[-1]
        tb.insert('1.0', body)
        tb.configure(state='disabled', height=150)
        # Comments
        if comments:
            ctk.CTkLabel(scroll, text=f"{self._t('comments')} ({len(comments)})",
                         font=F['heading'], text_color=C['text']).pack(anchor='w', pady=(10, 4))
            for c in comments:
                cf = ctk.CTkFrame(scroll, fg_color=C['card'], corner_radius=6,
                                   border_width=1, border_color=C['border'])
                cf.pack(fill='x', pady=3)
                user = c.get('user', {}).get('login', '')
                time_str = c.get('created_at', '')[:10]
                ctk.CTkLabel(cf, text=f"{user}  |  {time_str}", font=F['small'],
                             text_color=C['text3'], anchor='w').pack(fill='x', padx=10, pady=(6, 0))
                ctk.CTkLabel(cf, text=c.get('body', '')[:500], font=F['body'],
                             text_color=C['text'], anchor='w', wraplength=650,
                             justify='left').pack(fill='x', padx=10, pady=(2, 8))

    def _translate_text(self, text, direction):
        engine = self.config.get_translate_engine()
        if engine == 'baidu':
            return self._translate_baidu(text, direction)
        return self._translate_google(text, direction)

    def _translate_google(self, text, direction):
        from deep_translator import GoogleTranslator
        src = 'zh-CN' if direction == 'zh_en' else 'en'
        tgt = 'en' if direction == 'zh_en' else 'zh-CN'
        return GoogleTranslator(source=src, target=tgt).translate(text)

    def _translate_baidu(self, text, direction):
        import hashlib, random
        appid = self.config.get_baidu_appid()
        key = self.config.get_baidu_key()
        if not appid or not key:
            raise Exception("请先在设置中配置百度翻译 App ID 和密钥")
        src = 'zh' if direction == 'zh_en' else 'en'
        tgt = 'en' if direction == 'zh_en' else 'zh'
        salt = str(random.randint(32768, 65536))
        sign_str = appid + text + salt + key
        sign = hashlib.md5(sign_str.encode()).hexdigest()
        r = requests.post('http://api.fanyi.baidu.com/api/trans/vip/translate',
                          data={'q': text, 'from': src, 'to': tgt,
                                'appid': appid, 'salt': salt, 'sign': sign},
                          timeout=15)
        result = r.json()
        if 'trans_result' in result:
            return '\n'.join(item['dst'] for item in result['trans_result'])
        raise Exception(result.get('error_msg', '翻译失败'))

    def _open_url2(self, url):
        if url:
            import webbrowser
            webbrowser.open(url)

    # ==================== Settings Page ====================

    def _build_settings_page(self):
        p = self.pages['settings']
        self._section_label(p, self._t('settings'))

        card = self._card(p)
        inner = ctk.CTkFrame(card, fg_color='transparent')
        inner.pack(fill='x', padx=20, pady=15)

        # Dir
        r = ctk.CTkFrame(inner, fg_color='transparent')
        r.pack(fill='x', pady=6)
        ctk.CTkLabel(r, text=self._t('download_dir'), font=F['body'], width=100, anchor='w').pack(side='left')
        self.setting_dir = ctk.StringVar(value=self.config.get_download_dir())
        ctk.CTkEntry(r, textvariable=self.setting_dir, fg_color=C['card'],
                     border_color=C['border']).pack(side='left', fill='x', expand=True, padx=8)
        ctk.CTkButton(r, text=self._t('browse'), command=lambda: self._browse('setting_dir'),
                      fg_color=C['hover'], hover_color=C['border'],
                      width=55, height=28, corner_radius=6, font=F['small'],
                      text_color=C['text']).pack(side='left')

        # Workers
        r2 = ctk.CTkFrame(inner, fg_color='transparent')
        r2.pack(fill='x', pady=6)
        ctk.CTkLabel(r2, text=self._t('concurrency'), font=F['body'], width=100, anchor='w').pack(side='left')
        self.setting_workers = ctk.StringVar(value=str(self.config.get_max_workers()))
        ctk.CTkOptionMenu(r2, variable=self.setting_workers, values=[str(i) for i in range(1,21)],
                          fg_color=C['card'], button_color=C['accent'], text_color=C['text'], width=70).pack(side='left', padx=8)

        # Rate
        r3 = ctk.CTkFrame(inner, fg_color='transparent')
        r3.pack(fill='x', pady=6)
        ctk.CTkLabel(r3, text="Rate Limit", font=F['body'], width=100, anchor='w').pack(side='left')
        self.setting_rate = ctk.StringVar(value=str(self.config.get_rate_limit()))
        ctk.CTkOptionMenu(r3, variable=self.setting_rate, values=[str(i) for i in range(1,11)],
                          fg_color=C['card'], button_color=C['accent'], text_color=C['text'], width=70).pack(side='left', padx=8)
        ctk.CTkLabel(r3, text="秒", font=F['body']).pack(side='left')

        # Token
        r4 = ctk.CTkFrame(inner, fg_color='transparent')
        r4.pack(fill='x', pady=6)
        ctk.CTkLabel(r4, text="GitHub Token", font=F['body'], width=100, anchor='w').pack(side='left')
        self.setting_token = ctk.StringVar(value=self.config.get_github_token())
        self.token_entry = ctk.CTkEntry(r4, textvariable=self.setting_token,
                                         fg_color=C['card'], border_color=C['border'], show="*")
        self.token_entry.pack(side='left', fill='x', expand=True, padx=8)
        self._tok_vis = False
        def toggle():
            self._tok_vis = not self._tok_vis
            self.token_entry.configure(show="" if self._tok_vis else "*")
            tog.configure(text="隐藏" if self._tok_vis else "显示")
        tog = ctk.CTkButton(r4, text="显示", command=toggle,
                             fg_color=C['hover'], hover_color=C['border'],
                             width=50, height=28, corner_radius=6, font=F['small'],
                             text_color=C['text'])
        tog.pack(side='left')

        ctk.CTkLabel(inner, text="可选: 配置后 API 速率 10次/分 → 30次/分",
                     font=F['caption'], text_color=C['text3']).pack(anchor='w', pady=(2, 8))

        ctk.CTkFrame(inner, fg_color=C['divider'], height=1).pack(fill='x', pady=8)

        # Language
        r5 = ctk.CTkFrame(inner, fg_color='transparent')
        r5.pack(fill='x', pady=6)
        ctk.CTkLabel(r5, text=self._t('ui_lang_label'), font=F['body'], width=100, anchor='w').pack(side='left')
        lang_map = {'中文': 'zh', 'English': 'en', '日本語': 'ja', '한국어': 'ko',
                    'Français': 'fr', 'Deutsch': 'de', 'Español': 'es'}
        lang_names = list(lang_map.keys())
        current_lang = self.config.get_ui_language()
        current_lang_name = [k for k, v in lang_map.items() if v == current_lang]
        self.setting_lang = ctk.StringVar(value=current_lang_name[0] if current_lang_name else '中文')
        self._lang_map = lang_map
        ctk.CTkOptionMenu(r5, variable=self.setting_lang, values=lang_names,
                          fg_color=C['card'], button_color=C['accent'], text_color=C['text'], width=120).pack(side='left', padx=8)

        # Translate engine
        r6 = ctk.CTkFrame(inner, fg_color='transparent')
        r6.pack(fill='x', pady=6)
        ctk.CTkLabel(r6, text=self._t('trans_engine_label'), font=F['body'], width=100, anchor='w').pack(side='left')
        engine_map = {'Google Translate': 'google', '百度翻译': 'baidu'}
        engine_names = list(engine_map.keys())
        current_engine = self.config.get_translate_engine()
        current_engine_name = [k for k, v in engine_map.items() if v == current_engine]
        self.setting_engine = ctk.StringVar(value=current_engine_name[0] if current_engine_name else 'Google Translate')
        self._engine_map = engine_map
        ctk.CTkOptionMenu(r6, variable=self.setting_engine, values=engine_names,
                          fg_color=C['card'], button_color=C['accent'], text_color=C['text'], width=180).pack(side='left', padx=8)

        # Baidu App ID
        r7 = ctk.CTkFrame(inner, fg_color='transparent')
        r7.pack(fill='x', pady=6)
        ctk.CTkLabel(r7, text=self._t('baidu_appid_label'), font=F['body'], width=100, anchor='w').pack(side='left')
        self.setting_baidu_appid = ctk.StringVar(value=self.config.get_baidu_appid())
        ctk.CTkEntry(r7, textvariable=self.setting_baidu_appid, fg_color=C['card'],
                     border_color=C['border']).pack(side='left', fill='x', expand=True, padx=8)

        # Baidu Key
        r8 = ctk.CTkFrame(inner, fg_color='transparent')
        r8.pack(fill='x', pady=6)
        ctk.CTkLabel(r8, text=self._t('baidu_key_label'), font=F['body'], width=100, anchor='w').pack(side='left')
        self.setting_baidu_key = ctk.StringVar(value=self.config.get_baidu_key())
        ctk.CTkEntry(r8, textvariable=self.setting_baidu_key, fg_color=C['card'],
                     border_color=C['border']).pack(side='left', fill='x', expand=True, padx=8)

        ctk.CTkLabel(inner, text="百度翻译需要 App ID 和密钥 (免费申请: fanyi.baidu.com)",
                     font=F['caption'], text_color=C['text3']).pack(anchor='w', pady=(2, 8))

        ctk.CTkButton(inner, text=self._t('save_settings'), command=self._save_settings,
                      fg_color=C['accent'], hover_color=C['accent_hover'],
                      font=F['body'], height=34, corner_radius=6).pack(pady=10)

        ctk.CTkLabel(inner, text=f"配置文件: {self.config.config_file}",
                     font=F['caption'], text_color=C['text3']).pack(anchor='w')

    def _browse(self, var):
        d = filedialog.askdirectory()
        if d:
            getattr(self, var).set(d)

    def _save_settings(self):
        try:
            self.config.set_download_dir(self.setting_dir.get())
            self.config.set_max_workers(int(self.setting_workers.get()))
            self.config.set_rate_limit(float(self.setting_rate.get()))
            self.config.set_github_token(self.setting_token.get())
            self.url_download_dir.set(self.setting_dir.get())
            self.github_download_dir.set(self.setting_dir.get())
            t = self.setting_token.get().strip() or None
            self.crawler = GitHubTrendingCrawler(token=t)
            self.searcher = RepoSearcher(token=t)
            # Language & translation
            new_lang = self._lang_map.get(self.setting_lang.get(), 'zh')
            old_lang = self.config.get_ui_language()
            self.config.set_ui_language(new_lang)
            new_engine = self._engine_map.get(self.setting_engine.get(), 'google')
            self.config.set_translate_engine(new_engine)
            self.config.set_baidu_appid(self.setting_baidu_appid.get())
            self.config.set_baidu_key(self.setting_baidu_key.get())
            if new_lang != old_lang:
                messagebox.showinfo("成功", "设置已保存。语言已更改，请重启程序生效。")
            else:
                messagebox.showinfo("成功", "设置已保存")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def load_config(self):
        self.url_download_dir.set(self.config.get_download_dir())
        self.github_download_dir.set(self.config.get_download_dir())

    # ==================== Trending ====================

    def _fetch_trending(self):
        def _run():
            try:
                self.after(0, lambda: self.status_var.set("获取热榜..."))
                repos = self.crawler.fetch_trending(
                    since=self.trending_since.get(),
                    language=self.trending_lang.get() or None)
                if repos:
                    self.current_repos = repos[:int(self.trending_limit.get())]
                    self.after(0, lambda: self._fill_trending(self.current_repos))
                    self.after(0, lambda: self.status_var.set(f"共 {len(self.current_repos)} 个仓库"))
                else:
                    token = self.config.get_github_token()
                    if not token:
                        self.after(0, lambda: self.status_var.set("API 速率限制，请到设置填写 GitHub Token"))
                        self.after(0, lambda: messagebox.showwarning("速率限制",
                            "GitHub API 已达到无认证限制 (10次/分钟)\n\n"
                            "请到「设置」页面填写 GitHub Token\n"
                            "填写后限制提升到 30次/分钟\n\n"
                            "Token 获取: GitHub → Settings → Developer settings\n"
                            "→ Personal access tokens → Generate new token"))
                    else:
                        self.after(0, lambda: self.status_var.set("未获取到数据，请稍后再试"))
            except Exception as e:
                self.after(0, lambda: self.status_var.set(f"失败: {e}"))
        threading.Thread(target=_run, daemon=True).start()

    def _fill_trending(self, repos):
        self.trending_tree.delete(*self.trending_tree.get_children())
        for i, r in enumerate(repos, 1):
            self.trending_tree.insert('', 'end', values=(
                '☑', r.get('name',''), r.get('language',''),
                f"{r.get('stars',0):,}", f"{r.get('forks',0):,}",
                r.get('description','')[:55], "下载"))

    # ==================== Search ====================

    def _search_repos(self):
        def _run():
            try:
                q = self.search_query.get()
                if not q:
                    self.after(0, lambda: self.status_var.set("请输入关键词"))
                    return
                self.after(0, lambda: self.status_var.set(f"搜索: {q}..."))
                results = self.searcher.search(
                    q, limit=int(self.search_limit.get()),
                    language=self.search_lang.get() or None)
                if results:
                    self.current_repos = results
                    self.after(0, lambda: self._fill_search(results))
                    self.after(0, lambda: self.status_var.set(f"找到 {len(results)} 个仓库"))
                else:
                    self.after(0, lambda: self.status_var.set("无结果"))
            except Exception as e:
                self.after(0, lambda: self.status_var.set(f"失败: {e}"))
        threading.Thread(target=_run, daemon=True).start()

    def _fill_search(self, repos):
        self.search_tree.delete(*self.search_tree.get_children())
        for i, r in enumerate(repos, 1):
            self.search_tree.insert('', 'end', values=(
                '☑', r.get('name',''), r.get('owner',''), r.get('language',''),
                f"{r.get('stars',0):,}", f"{r.get('forks',0):,}", "下载"))


def main():
    app = GitHubCrawlerGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
