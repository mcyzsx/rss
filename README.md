# Gmerss
Gmerss is a RSS-Reader All in Github

## 拉取条件

### 时间范围
- **默认拉取最近 7 天的文章**
- 可通过修改 `displayDay` 变量调整时间范围

### 每个 RSS 源限制
- **每个 RSS 源最多拉取 2 篇文章**
- 可通过修改 `displayMax` 变量调整数量

### RSS 源配置

当前配置的 RSS 源：

| 名称 | URL | 时间格式 | 状态 |
|------|-----|----------|------|
| 安知鱼 | https://blog.anheyu.com/rss.xml | `%a, %d %b %Y %H:%M:%S +0000` | 正常 |
| 张洪heo | https://blog.zhheo.com/rss.xml | `%a, %d %b %Y %H:%M:%S GMT` | 正常 |
| 纸鹿 | https://blog.zhilu.site/atom.xml | `%Y-%m-%dT%H:%M:%SZ` | 正常 |
| APP喵 | https://www.appmiao.com/feed | `%a, %d %b %Y %H:%M:%S +0000` | 正常 |
| Meekdai | https://blog.meekdai.com/rss.xml | `%a, %d %b %Y %H:%M:%S +0000` | 正常 |

### 拉取失败原因

如果某个 RSS 源没有拉取到内容，可能的原因：

1. **网络连接问题**
   - 服务器拒绝连接（Connection reset by peer）
   - 服务器限制了 GitHub Actions 的 IP 地址
   - 解决方案：代码已添加 `requests` 库和浏览器 User-Agent 尝试解决

2. **文章时间过旧**
   - 该 RSS 源最近 7 天内没有更新文章
   - 日志会显示 "Entry too old, skipping"
   - 这是正常情况，不是代码问题

3. **时间格式不匹配**
   - RSS 源的时间格式与配置不符
   - 代码会自动尝试多种时间格式解析

### 调试信息

运行时会输出详细的调试信息：
- Feed 状态码
- 条目数量
- 可用的日期字段
- 尝试的时间格式
- 解析后的时间戳
- 跳过原因（太新/太旧）

### 依赖安装

```bash
pip install requests feedparser
```
