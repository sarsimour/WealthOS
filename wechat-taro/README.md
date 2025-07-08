# WealthOS WeChat Mini Program (Taro版)

基于 **Taro + React + TypeScript** 开发的微信小程序版本。这是一个现代化的投资理财应用，提供实时加密货币价格查看和投资组合管理。

## 🎯 **项目亮点**

- ✅ **Taro框架**: 使用React开发，编译为原生小程序
- ✅ **TypeScript**: 完整类型安全
- ✅ **实时数据**: 真实的Bitcoin价格API集成
- ✅ **Canvas图表**: 原生Canvas绘制价格趋势图
- ✅ **响应式设计**: 现代化金融应用界面
- ✅ **下拉刷新**: 原生小程序交互
- ✅ **WeChat AppID**: 需要配置你的小程序AppID

## 🏗️ **技术栈**

```
前端: Taro 4.1.2 + React 18 + TypeScript + Sass
构建: Vite + Babel
后端: FastAPI (Python) - 复用现有WealthOS后端
图表: 原生Canvas 2D API
包管理: pnpm
```

## 🚀 **完整运行指南**

### **前提条件**
- ✅ 已安装微信开发者工具
- ✅ 已注册微信小程序并获取AppID
- ✅ 后端已配置并运行在端口 8101

### **Step 0: 配置项目**

```bash
# 复制配置文件模板
cp project.config.json.template project.config.json

# 编辑配置文件，替换YOUR_WECHAT_APPID_HERE为你的实际AppID
# 例如: "appid": "wxYOUR_ACTUAL_APPID_HERE"
```

---

### **Step 1: 启动后端服务**

```bash
# 进入后端目录
cd ../backend

# 激活虚拟环境
source .venv/bin/activate

# 启动后端 (端口 8101)
python -m app.main
```

**验证后端:**
```bash
curl http://localhost:8101/health
# 应返回: {"status":"healthy"}

curl "http://localhost:8101/api/v1/prices/crypto/btc?vs_currency=usd"
# 应返回: Bitcoin价格数据
```

---

### **Step 2: 开发模式运行**

```bash
# 在 wechat-taro 目录
cd wechat-taro

# 安装依赖 (如果还没安装)
pnpm install

# 开发模式 - 实时编译
pnpm dev:weapp
```

---

### **Step 3: 生产构建**

```bash
# 构建小程序
pnpm build:weapp

# 构建产物在 dist/ 目录
ls -la dist/
```

---

### **Step 4: 微信开发者工具配置**

1. **打开微信开发者工具**
2. **导入项目:**
   ```
   项目目录: /Users/s/Projects/WealthOS/wechat-taro/dist
   AppID: 使用你在project.config.json中配置的AppID
   项目名称: WealthOS
   ```
3. **开发设置:**
   - 关闭域名校验 (开发阶段)
   - 启用ES6转ES5
   - 启用增强编译

---

## 📱 **功能特性**

### **🏠 首页 - 投资组合概览**
- 总资产显示和收益统计
- 实时Bitcoin价格更新
- 快速操作入口
- 持仓列表预览
- 市场快讯

### **📊 行情页 - Bitcoin价格图表**
- 实时Bitcoin价格显示
- Canvas绘制的价格趋势图
- 多时间周期切换 (1天/7天/30天/90天)
- 下拉刷新功能
- 24小时高低价和市场数据

### **💰 投资组合页** (占位页面)
- 待开发：详细持仓管理

### **👤 个人中心页** (占位页面)
- 待开发：用户设置和账户信息

---

## 🔧 **开发指南**

### **项目结构**
```
wechat-taro/
├── src/
│   ├── pages/           # 页面组件
│   │   ├── index/      # 首页
│   │   ├── market/     # 行情页
│   │   ├── portfolio/  # 投资组合
│   │   └── profile/    # 个人中心
│   ├── utils/          # 工具函数
│   │   └── api.ts      # API请求封装
│   ├── types/          # TypeScript类型定义
│   ├── app.config.ts   # 应用配置
│   └── app.ts          # 应用入口
├── dist/               # 构建产物
├── config/             # 构建配置
└── project.config.json # 小程序项目配置
```

### **API集成**
```typescript
import { api } from '../utils/api'

// 获取Bitcoin价格
const price = await api.getBitcoinPrice()

// 获取历史数据
const history = await api.getBitcoinHistory('7d')

// 健康检查
const health = await api.healthCheck()
```

### **添加新页面**
1. 在 `src/pages/` 创建新目录
2. 添加 `index.tsx` 和 `index.scss`
3. 在 `app.config.ts` 中注册页面路径

---

## 🔄 **开发工作流**

### **实时开发**
```bash
# 启动开发模式
pnpm dev:weapp

# 在微信开发者工具中打开 dist/ 目录
# 代码更改会自动重新编译
```

### **调试技巧**
- 使用微信开发者工具的调试功能
- Console输出在开发者工具中查看
- 网络请求在Network面板监控
- 使用真机调试测试Canvas功能

---

## 🌟 **Taro vs 原生小程序的优势**

| 特性 | Taro (React) | 原生小程序 |
|------|-------------|-----------|
| 开发语言 | TypeScript/JSX | JavaScript/WXML |
| 组件系统 | React组件 | 小程序组件 |
| 状态管理 | React Hooks | Page data |
| 代码重用 | ✅ 可与Web共享 | ❌ 小程序专用 |
| 开发体验 | ✅ 现代化工具链 | ❌ 传统开发 |
| 类型安全 | ✅ TypeScript | ❌ 需手动配置 |
| 热重载 | ✅ 支持 | ❌ 需手动刷新 |

---

## 🚨 **故障排除**

### **常见问题**

1. **构建失败**
   ```bash
   # 清理缓存重新安装
   rm -rf node_modules pnpm-lock.yaml
   pnpm install
   ```

2. **API请求失败**
   ```bash
   # 确认后端运行状态
   curl http://localhost:8101/health
   
   # 检查微信开发者工具域名校验设置
   ```

3. **Canvas图表不显示**
   - 确保使用真机调试
   - Canvas在模拟器中可能有问题

4. **小程序加载失败**
   - 检查AppID配置
   - 确认 `dist/` 目录有构建产物
   - 重新构建: `pnpm build:weapp`

---

## 📈 **性能优化**

- 图片资源懒加载
- API请求缓存机制
- Canvas绘制性能优化
- 包体积分析: `pnpm build:weapp --analyze`

---

## 🔮 **后续开发计划**

- [ ] 完善投资组合页面
- [ ] 添加用户认证
- [ ] 支持更多加密货币
- [ ] 添加价格提醒功能
- [ ] 集成微信支付
- [ ] 数据离线缓存

---

## 📞 **技术支持**

如有问题，请检查：
1. 后端API是否正常运行
2. 微信开发者工具配置
3. 网络连接状态
4. 构建产物是否最新

**快速验证命令:**
```bash
# 后端健康检查
curl http://localhost:8101/health

# 重新构建
pnpm build:weapp

# 查看构建产物
ls -la dist/
``` 