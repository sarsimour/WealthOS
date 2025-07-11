# 项目代号：“省心投” 产品核心理念与功能框架 V1.0

**文档目的：** 本文档旨在明确“省心投”项目的核心价值主张、目标用户画像及产品设计原则，为产品、设计、研发团队提供统一的指导纲领，确保所有功能开发都严格服务于最终目标。

**最终目标：帮助普通投资者“少亏钱，尽量赚钱”。**

---

## 第一章：核心用户画像 (The User Persona)

本项目所有设计的唯一出发点和最高准则，是服务于以下特征的“上帝用户”：

> **脾气非常大，智商非常低，而且非常没有耐心，又非常非常小气。**

#### **画像解读与设计映射：**

*   **脾气大 (Huge Temper):**
    *   **表现:** 遇挫（亏损、操作不顺）易怒，缺乏安全感，易迁怒于产品。
    *   **设计原则:** **零摩擦 + 强安抚**。任何让用户困惑、等待、多点一步的操作都是“原罪”。必须提供及时的、高情商的、安抚性的反馈，尤其是在用户亏钱时。

*   **智商低 (Low Financial Literacy):**
    *   **表现:** 无法理解金融术语，不明白复杂图表，只认最直观的涨跌和金额。
    *   **设计原则:** **零术语 + 强比喻**。产品中禁止出现“夏普比率”、“Alpha”、“Beta”等一切专业术语。所有概念必须用大白话、生活中的比喻来解释。例如：“资产配置”→“鸡蛋和篮子”，“波动率”→“过山车指数”。

*   **没耐心 (Extremely Impatient):**
    *   **表现:** 注意力持续时间极短，无法阅读长文，追求即时结果和反馈。
    *   **设计原则:** **短路径 + 即时反馈**。任何核心操作路径不能超过3步。内容呈现以短视频、动画、金句、漫画、单图为主。学习和任务必须有即时奖励（虚拟徽章、积分等）。

*   **非常小气 (Extremely Stingy):**
    *   **表现:** 对成本（手续费、服务费）极度敏感，渴望“占便宜”的感觉。
    *   **设计原则:** **成本可视化 + 价值感塑造**。必须清晰地展示所有费用，并量化地告诉用户，我们的方案能帮他“省下多少钱”。让用户感觉花在这里的时间和金钱是“值得的”。

---

## 第二章：核心功能模块详细设计 (Functional Modules Design)

#### **模块一：投资者教育系统 - “财富训练营”**

*   **核心目标:** 在用户无感、无压力的情况下，将核心投资理念（分散、长期、风控）植入其心智。
*   **关键功能点:**
    1.  **场景化Tips系统 (Quips & Bites):**
        *   **触发机制:** 由特定场景（如市场大跌/大涨、用户登录、用户准备交易时）触发，而非随机推送。
        *   **内容形式:** “金句 + 表情包/漫画”的形式。内容库需覆盖安抚、提醒、鼓励、警告等多种情绪。
        *   **交互:** 以轻量弹窗、通知栏消息等不打断主流程的形式出现。
    2.  **游戏化学习模块 (“训练营”):**
        *   **路径设计:** 采用线性闯关模式，每一关解决一个核心知识点。
        *   **关卡内容:** 60秒以内的动画/短视频 + 1-2道场景化选择题。
        *   **激励系统:** 通关后立即获得正反馈，如“避坑达人”、“长期主义者”等虚拟徽章和积分，营造收集和攀比的乐趣。

#### **模块二：AI虚拟投资顾问 - “私人陪聊”**

*   **核心目标:** 成为用户的“情绪垃圾桶”和“高情商投资教练”，在持续沟通中完成风险评估、投资建议和长期陪伴。
*   **关键功能点:**
    1.  **人格化设定 (Persona):**
        *   提供2-3种可选人设（如：“毒舌大爷”、“暖心学姐”），让用户选择自己偏好的沟通风格。
        *   AI的语言风格必须严格遵守选定的人设，保持一致性。
    2.  **对话式风险评估:**
        *   禁止使用问卷。通过模拟场景的聊天完成评估。例：“假如中了50万，你是先买房还是去梭哈一把？”
        *   AI需能理解用户的俚语、情绪化表达（如“亏麻了”、“求回本”），并给出符合人设和场景的回答。
    3.  **主动沟通机制:**
        *   在关键节点（市场剧烈波动、用户持仓比例严重偏离、定期定投扣款日）主动发起对话，提供安抚、建议或提醒。
    4.  **情绪价值优先:** 首要任务是接住用户的情绪，然后才是传递知识和建议。当用户表达愤怒时，第一反应是“我理解您”，而不是“根据数据显示”。

#### **模块三：投资建议与报告 - “一图流PPT”**

*   **核心目标:** 提供清晰易懂、视觉冲击力强、直击用户痛点的投资组合方案与分析报告。
*   **关键功能点:**
    1.  **组合方案命名:**
        *   必须口语化、场景化。如：“稳稳的幸福”养老组合、“年轻就要浪”高成长组合、“选择困难症”懒人组合。
    2.  **可视化报告:**
        *   **设计原则:** 像一份漂亮的PPT，而不是一份研报。多图少字，重点突出。
        *   **核心图表:**
            *   **收益模拟图:** 一条平滑向上的组合收益曲线，对比一条波动巨大的个股/单基金K线图。
            *   **风险对比图:** 用“最大可能亏多少钱”的直观图表，对比同类产品的风险。
            *   **资产分布饼图:** 简单明了地展示“鸡蛋都放在了哪些不同的篮子里”。
    3.  **成本计算器:**
        *   在方案页面显著位置，计算并展示“选择本方案对比您自己胡乱操作，一年大约可节省XXX元手续费”。
    4.  **AI一句话解读:**
        *   每个报告和方案，都由AI虚拟顾问提供一段“人话总结”，直接告诉用户“该不该买”、“有什么好处”、“要注意什么”。

#### **模块四：基础信息工具 - “风险置顶”的基金超市**

*   **核心目标:** 提供基础的基金查询功能，但通过信息展示的重新编排，从根本上引导用户关注风险而非短期收益。
*   **关键功能点:**
    1.  **基金详情页布局:**
        *   **第一屏（首要位置）:** **必须是风险指标**。用最大、最醒目的字体和颜色（如绿色）标出“历史最大回撤”、“近一年波动率”，并配上“这只基金最多会让你亏掉XX%”这样的人话解读。
        *   **第二屏及以后:** 才是基金经理、持仓、历史业绩等常规信息。
    2.  **收益率展示:**
        *   默认展示时间维度为“近3年”、“近5年”或“成立以来”，弱化“近1月”、“近3月”等短期指标的权重。
    3.  **搜索与排序:**
        *   在排序选项中，将“风险从低到高”、“回撤从小到大”置于靠前或默认位置。
        *   当用户主动搜索高风险主题基金（如“白酒”、“军工”、“券商”）时，搜索结果页顶部自动弹出高风险警告横幅。

---

## 第三章：总结 (Conclusion)

我们不是在做一个金融软件，我们是在做一个**“反人性”的投资行为矫正器**。我们的竞争对手不是其他基金App，而是用户自己“追涨杀跌、盲目自信”的本能。

**请务必将“上帝用户画像”打印出来，贴在每个人的工位上。** 每一个像素、每一行代码、每一句文案，都必须为了服务好这位“上帝”而存在。