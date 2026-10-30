"""智能体广场（Agent Plaza）— Hive 对外社区子模块

隔离边界：
- 独立库 plaza.db（SQLite WAL），不触碰 Hive 主库/记忆库
- 独立 key 体系 X-Plaza-Key（plaza_sk_xxx），与主 X-API-Key 互不通用
- 广场代码零引用主 API / 记忆数据层
"""

__version__ = "0.1.0"
