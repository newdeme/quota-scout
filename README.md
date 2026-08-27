# 🛰️ Free-Quota Radar · 免费模型额度雷达

自动化探测各官方渠道**合法免费额度**的可用性：GitHub Actions 定时实弹调用，状态直接呈现在本 README，不再需要人工维护"这个还能不能白嫖"的问题。

> 合规边界：只收录厂商**官方公开**的免费层 / 试用额度 / 赠送金。不收录任何逆向 Web 转 API 的灰色渠道。

<!-- RADAR:START -->
| 渠道 | 分类 | 免费方式（快照，以官方为准） | 状态 | 延迟 | 最后探测 (UTC) | 密钥变量 | 注册 |
|---|---|---|---|---|---|---|---|
| [Google AI Studio (Gemini API)](https://aistudio.google.com/) | 国际 | 有永久免费层，按模型设每日/每分钟限额，适合个人体验与小规模开发 | ⚪ 待密钥 | — | — | `GEMINI_API_KEY` | [注册](https://aistudio.google.com/apikey) |
| [OpenRouter (:free 模型)](https://openrouter.ai/) | 国际 | 带 :free 后缀的模型可免费调用（每日限额）；需注册并配置 API Key，2026-08 实测匿名调用已返回 401 | ⚪ 待密钥 | — | — | `OPENROUTER_API_KEY` | [注册](https://openrouter.ai/settings/keys) |
| [Groq Cloud](https://groq.com/) | 国际 | 开发者免费层，速率受限但长期可用，推理速度极快 | ⚪ 待密钥 | — | — | `GROQ_API_KEY` | [注册](https://console.groq.com/keys) |
| [Cerebras Inference](https://cloud.cerebras.ai/) | 国际 | 免费层提供每日较大 token 配额，主打超高速推理 | ⚪ 待密钥 | — | — | `CEREBRAS_API_KEY` | [注册](https://cloud.cerebras.ai/) |
| [Mistral La Plateforme](https://mistral.ai/) | 国际 | Experiment 免费计划（需在控制台选择加入），有速率限制 | ⚪ 待密钥 | — | — | `MISTRAL_API_KEY` | [注册](https://console.mistral.ai/api-keys) |
| [NVIDIA NIM (build.nvidia.com)](https://build.nvidia.com/) | 国际 | 开发者计划赠送大量推理调用额度，开源模型家族齐全 | ⚪ 待密钥 | — | — | `NVIDIA_API_KEY` | [注册](https://build.nvidia.com/explore/discover) |
| [GitHub Models](https://github.com/marketplace/models) | 国际 | 任意 GitHub 账号可用 PAT 调用多家主流模型，按账号等级限速，免额外注册 | ⚪ 待密钥 | — | — | `GITHUB_MODELS_TOKEN` | [注册](https://github.com/settings/tokens) |
| [Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers) | 国际 | 所有注册用户每月附带少量免费推理 credit（约一周量级的轻度使用），超出后走付费 | ⚪ 待密钥 | — | — | `HF_TOKEN` | [注册](https://huggingface.co/settings/tokens) |
| [SiliconFlow 硅基流动](https://siliconflow.cn/) | 国内 | 注册赠送体验金，另有多个常驻免费小模型（Qwen/GLM 小尺寸等） | ⚪ 待密钥 | — | — | `SILICONFLOW_API_KEY` | [注册](https://cloud.siliconflow.cn/account/ak) |
| [ModelScope 魔搭社区](https://www.modelscope.cn/) | 国内 | 每日免费推理调用次数（刷新制），开源模型数量多，国内访问友好 | ⚪ 待密钥 | — | — | `MODELSCOPE_TOKEN` | [注册](https://www.modelscope.cn/my/myaccesstoken) |
| [智谱 BigModel 开放平台](https://open.bigmodel.cn/) | 国内 | glm-4-flash 等轻量模型长期免费调用 | ⚪ 待密钥 | — | — | `ZHIPU_API_KEY` | [注册](https://open.bigmodel.cn/usercenter/apikeys) |
| [阿里云百炼 DashScope](https://www.aliyun.com/product/bailian) | 国内 | 新用户各主流模型均有限时免费额度，部分通义小模型有常驻免费档 | ⚪ 待密钥 | — | — | `DASHSCOPE_API_KEY` | [注册](https://bailian.console.aliyun.com/?apiKey=1) |
| [百度千帆 ModelBuilder](https://qianfan.cloud.baidu.com/) | 国内 | 部分文心及开源模型提供限时免费试用额度（随活动变化，以控制台为准） | ⚪ 待密钥 | — | — | `QIANFAN_API_KEY` | [注册](https://console.bce.baidu.com/iam/#/iam/apikey/list) |
| [Cloudflare Workers AI](https://developers.cloudflare.com/workers-ai/) | 国际 | 每日免费 neuron 分配，可在 Workers 内或 REST 调用多模态开源模型 | 📖 收录未探测 | — | 2026-08-27T02:10:25Z | `CF_WORKERS_AI_TOKEN` | [注册](https://dash.cloudflare.com/profile/api-tokens) |
<!-- RADAR:END -->

## 状态图例

| 图标 | 含义 |
|---|---|
| ✅ | 实弹验证可用（已配密钥，调用成功） |
| 🟢 | 匿名调用成功 |
| 🟡 | 429 限流 —— 服务正常，只是达到速率上限 |
| ⚪ | 未配置密钥，跳过探测 |
| 🔑 | 密钥被拒（401/403） |
| 🏷️ | 模型 ID 失效，需更新 `data/channels.json` |
| 💸 | 额度耗尽 |
| ❌ | 不可用（网络失败 / 5xx） |
| 📖 | 手册收录，暂无自动探活 |

## 工作原理

```
data/channels.json   渠道登记表（模型 ID、端点、免费方式快照、密钥变量名）
scripts/probe.py     探活：向每个渠道发一条 max_tokens=8 的 "ping"
scripts/render.py    把结果渲染成 README 状态表 + shields.io 徽章数据
.github/workflows/   cron 每 6 小时跑 probe → render → 自动 commit
data/history.jsonl   每次探测的滚动历史（可用于画趋势图）
```

## 使用

1. Fork / Clone 本仓库
2. （可选）在仓库 Settings → Secrets 中添加你想验证的渠道密钥，变量名见表格"密钥变量"列；不配置则显示 ⚪ 待密钥
3. Actions 默认开启，每 6 小时自动刷新；也可手动 Dispatch

本地运行：

```bash
cp .env.example .env   # 填入你手里的 key（.env 已 gitignore）
python3 scripts/probe.py                # 全量
python3 scripts/probe.py --only groq    # 单测一个渠道
```

## 贡献新渠道

给 `data/channels.json` 提 PR 即可，字段要求见现有条目。硬性标准：

1. **官方免费层或明确公示的试用额度**（合规红线）
2. 提供 OpenAI 兼容 chat completions 端点者优先（可被自动探活）
3. `free_tier` 描述写明限额性质（每日刷新 / 月度 credit / 注册赠送一次）

## 免责声明

- 表格中的免费额度描述为撰写时快照，厂商随时调整，一切以官方页面为准。
- 探活请求极小（8 token），但请勿滥用免费额度；本工具不代理、不分发任何密钥。
