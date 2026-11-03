# DS Quest · 数据结构闯关

一个**给自己用**的本地数据结构学习平台。不是又一个 OJ，而是把"看懂 → 抄会 → 写出来 → 知道自己错在哪"这条链路做完整。

- 学习地图：11 个关卡，按你们课的实际章节排（绪论 / 线性表 / 栈与队列 / 串 / 矩阵 / 散列 / 树 / BST·红黑树 / 图 / 排序 / 上机真题），当前开放前 3 关和上机真题
- 知识点：18 节，每节都是通俗解释 + 课件术语 + 考点 + 易错点 + 复杂度表
- 代码库：9 份 C++ 模板，**写法严格对齐课件**（ArrayLinearList、Chain、循环队列的 front/rear 约定……），逐段解释 + 点击高亮对应代码行 + 一键复制
- 上机真题：2019-2020 上机题目汇编，已整理 6 道可判题（符号配对、出栈序列、KMP、稀疏矩阵、哈希平方探测、二叉树重构）
- 可视化：顺序表插入删除、栈的进出、循环队列的 front/rear 绕圈，都能一步一步看
- 判题：真实 g++ 编译运行，**失败时直接告诉你哪组输入、期望什么、你输出了什么**，还会做免费的中文编译错误解释和本地错因检查
- AI 助教：DeepSeek，**只有你点按钮才会调用**，有缓存、有每日上限、能本地算的绝不用 API
- 学习记录：XP、通关状态、错题本、笔记，全部本地 SQLite

---

## 一、怎么启动

### 已经装好依赖的情况下（这台电脑现在就是）

双击项目根目录的 **`start.bat`**，或者右键 `scripts/start.ps1` → 用 PowerShell 运行。

浏览器会自动打开 <http://127.0.0.1:8000>。

### 换一台电脑 / 想重新装

双击 **`setup.bat`**（或在 PowerShell 里跑 `scripts/setup.ps1`），它会依次：

1. 把 Python 依赖装进 `backend/vendor`（不污染系统环境）
2. 安装前端依赖（pnpm）
3. 构建前端到 `frontend/dist`

然后双击 `start.bat`。

> 需要：Python 3.10+、Node.js 18+、MinGW-w64 的 g++（判题用）。
> 检查 g++ 是否可用：命令行执行 `g++ --version`。

### 端口

默认 8000。想改就设环境变量 `DSQ_PORT`，或者在 `backend/.env` 里写 `DSQ_PORT=8001`。

---

## 二、启用 AI 助教（可选，不启用也能用）

1. 去 <https://platform.deepseek.com> 申请 API Key。
2. 复制 `backend/.env.example` 为 `backend/.env`，填入：

   ```
   DEEPSEEK_API_KEY=sk-你的key
   DSQ_AI_DAILY_LIMIT=30
   ```

3. 重启服务。

**没填 Key 会怎样？** 页面照常能用，只有"问 AI 助教"按钮会提示未启用。免费的题库提示、本地错因检查、参考解都不受影响。

### 为什么不会烧钱

| 机制 | 说明 |
| --- | --- |
| 被动触发 | 打开页面、切换知识点、运行代码、判题，**都不会**调用 API。只有点「让 AI 看看我的代码」才发请求 |
| 能本地算就不用 API | 第 1 层提示来自题库；「参考思路」直接返回题库里的参考解，0 成本；编译错误中文解释、格式串/数组越界等检查都是本地规则 |
| 缓存 | 同一道题 + 同一份代码 + 同一个问题，第二次直接命中缓存 |
| 每日上限 | 默认 30 次，用满就停，第二天自动重置。页头会显示剩余次数 |
| 长度限制 | `max_tokens` 默认 1200，回答被要求控制在 350 字以内 |

---

## 三、目录结构

```
DS-Quest/
├─ start.bat / setup.bat        给 Windows 用的一键脚本
├─ scripts/
│   ├─ start.ps1                启动服务（会自动选 Python、检查前端产物、开浏览器）
│   ├─ setup.ps1                安装依赖 + 构建前端
│   ├─ dev.ps1                  开发模式：后端热重载 + Vite 前端（5173）
│   └─ verify.ps1               跑内容自检 + 接口冒烟测试
├─ backend/
│   ├─ run.py                   后端启动入口（python backend/run.py）
│   ├─ verify.py                ★ 内容自检：用参考解真跑一遍所有测试点
│   ├─ smoke_test.py            接口冒烟测试
│   ├─ requirements.txt
│   ├─ .env.example             API Key 模板（复制成 .env 使用）
│   ├─ vendor/                  FastAPI 等依赖装在这里，不污染系统 Python
│   ├─ data/dsquest.db          学习进度、错题、提交记录（删掉=重置）
│   ├─ content/                 ★ 所有学习内容
│   │   ├─ modules.json         学习地图上的 11 个关卡
│   │   ├─ linear-list/
│   │   │   ├─ module.json      章节介绍
│   │   │   ├─ knowledge/*.md   知识点（Markdown，带 front matter）
│   │   │   ├─ code/*.cpp|*.c   代码模板正文
│   │   │   ├─ templates.json   代码模板的说明、逐段解释、常见错误
│   │   │   └─ problems/*.json  题目：描述 + 样例 + 测试数据 + 参考解
│   │   └─ stack-queue/         同上（栈 + 队列 8 个知识点、7 份代码、9 道题）
│   └─ app/
│       ├─ main.py              FastAPI 路由
│       ├─ content.py           内容加载
│       ├─ judge.py             ★ 编译 / 运行 / 比对 / 编译错误翻译
│       ├─ ai.py                DeepSeek 调用、缓存、额度、免费静态检查
│       ├─ store.py             SQLite
│       └─ config.py            配置
└─ frontend/
    ├─ src/views/               页面：地图 / 章节 / 知识点 / 题目 / 错题本
    ├─ src/components/          编辑器、判题结果、可视化、AI 抽屉……
    └─ dist/                    构建产物（后端会直接托管它）
```

---

## 四、内容是怎么组织的（以后加章节看这里）

### 加一个知识点

在 `backend/content/<模块>/knowledge/` 下新建 `06-xxx.md`：

```markdown
---
id: xxx
title: 标题
summary: 一句话摘要
minutes: 12
tags: 标签1, 标签2
exam: 这道题会怎么考
group: 分组名
---

## 正文
正常写 Markdown 就行。支持表格、代码块、引用，以及这些提示块：

:::exam 常见考点
这一块会渲染成紫色的考点卡片
:::

:::pitfall 易错点
红色卡片
:::
```

还支持 `:::tip`、`:::note`、`:::warning`。

### 加一道题

在 `problems/` 下新建 `ll-07.json`，照着现有的文件抄结构。**最关键的是 `tests`**：

```json
{
  "id": "ll-07",
  "title": "题目名",
  "difficulty": 2,
  "tags": ["顺序表"],
  "statement": "题面（Markdown）",
  "inputFormat": "...",
  "outputFormat": "...",
  "samples": [{ "input": "...", "output": "...", "explain": "..." }],
  "hints": ["提示1（免费）", "提示2", "提示3"],
  "starterCode": "给学生的初始模板",
  "solution": "参考解（会被自检脚本真的编译运行）",
  "tests": [
    { "name": "样例 1", "input": "...", "output": "..." },
    { "name": "边界：空表", "input": "...", "output": "..." }
  ],
  "knowledgeIds": ["seqlist"],
  "timeLimitMs": 2000
}
```

写完**一定要跑一遍自检**：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/verify.ps1
```

它会做三件事：

1. 把每道题的参考解真的编译、跑过所有测试点，输出不一致就报错（防止"题面说一套、数据是另一套"）；
2. 把代码库里所有模板编译一遍（防止贴给学生一段编译不过的代码）；
3. 检查模板里的高亮锚点、知识点引用是否存在。

**这一步是整个项目质量的保险丝。** 我写内容时就是靠它抓出了两道题的标准答案是错的。

### 加一个章节

1. 在 `modules.json` 里把对应条目的 `status` 改成 `"open"`；
2. 建同名目录，放 `module.json`、`knowledge/`、`code/`、`templates.json`、`problems/`；
3. 重启服务。

---

## 五、判题是怎么做的（以及安全边界）

一次提交的流程：

```
提交代码 → 写进 backend/data/runs/run-xxxx/main.cpp
        → g++ -O2 -static 编译（超时 25s）
        → 每个测试点：单独跑一次，stdin/stdout 走文件
        → 限制：CPU/墙钟超时、内存上限（Windows Job Object）、进程数、输出长度
        → 归一化比对（忽略行尾空格和末尾空行）
        → 只展示出错测试点的输入/期望/实际，避免"看不到错在哪"
```

编译错误会被解析成「第几行 + 中文原因 + 怎么改」，例如：

| 编译器说 | 页面显示 |
| --- | --- |
| `'x' was not declared in this scope` | 名字没定义或作用域不对：检查变量名拼写、是否在声明前使用了 |
| `expected ';' before` | 少了一个分号：看报错行号的**上一行**末尾 |
| `expected '}' at end of input` | 花括号不配对 |
| `no matching function for call to` | 函数调用的参数对不上 |

:::warning 安全边界（请认真看这一段）
程序是以**你自己的 Windows 账户**运行的，隔离手段是：

- 独立临时目录（跑完就删）
- Windows Job Object 限制内存 / 进程数 / 超时强杀
- 输出长度上限
- **没有**虚拟机、没有容器、没有独立低权限账户

对"自己写代码、自己判题"这个场景够用，但**不要把这个后端直接开给别人用**。
如果以后要让别人访问，把 `judge.py` 里的执行方式换成下面任意一种再上线：

- WSL2 + bubblewrap / nsjail（推荐，Linux 下最省事）
- Docker + `--network none --memory 256m --pids-limit 64 --read-only`
- 单独建一个低权限 Windows 用户，用 `runas` 以该用户启动编译产物
:::

---

## 六、常见问题

**Q：双击 start.bat 一闪而过？**
右键 →「在终端中运行」，或者打开 PowerShell 手动执行 `scripts/start.ps1`，就能看到报错信息。

**Q：页面提示"连不上后端"？**
后端没起来，或者端口被占用。看启动窗口里的报错；换端口的话在 `backend/.env` 写 `DSQ_PORT=8001`。

**Q：判题一直"编译错误"，但我明明在 Dev-C++ 里能跑？**
看页面上的中文提示。最常见的是用了 GCC 5.1 不支持的新特性（这台机器上是 TDM-GCC 5.1）。判题会自动按编译器版本选 `-std`，所以你如果写了 C++17 的结构化绑定 `auto [a,b]`，它会报错——换成 `pair` 就行。想用新特性就装个新版 MinGW-w64。

**Q：AI 说"额度已用完"？**
改 `backend/.env` 里的 `DSQ_AI_DAILY_LIMIT`，或等明天。缓存命中不扣额度。

**Q：想重置所有学习记录？**
删掉 `backend/data/dsquest.db`，重启服务。

**Q：Monaco 编辑器加载不出来？**
会自动降级成普通文本框，判题不受影响。要修的话重新 `pnpm install` 并重新 `build`。

---

## 七、GitHub

仓库：<https://github.com/enming-066/DS-Quest>（`main` 分支，已配置好 `origin`）

以后改完内容，更新到 GitHub 就三步：

```powershell
git add .
git commit -m "content: 补充某某章节"
git push
```

`.gitignore` 已经排除了 `backend/vendor`、`node_modules`、`dist`、`data`、`.env` 和临时目录，
**API Key 不会被提交**（仓库里只有 `backend/.env.example` 模板）。别人 clone 下来跑 `setup.bat` 就能装好。

---

## 八、下一步可以加什么

- 绪论 / 串 / 树 / 图 / 查找 / 排序 六个章节（内容结构已经定好，往里填就行）
- 把老师的 PPT、历年卷子里的题目整理成 `problems/*.json`（判题能直接用）
- 选择题模式（现在只有编程题，期末还有大量选择/填空/画图题）
- 复习计划：按错题和遗忘曲线排每天该看什么
- 提交历史对比：同一道题不同版本的代码 diff

这些都不需要改架构，属于"往 content 里加东西"或"加一个页面"的量级。
