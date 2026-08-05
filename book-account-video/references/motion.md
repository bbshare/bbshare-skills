# Motion Design — 读书号动效规范

## Mode A（默认）：少切镜、多层呼吸

爆款主体几乎不靠硬切炫技，靠 **慢推 + 粒子 + 片头**。

### 最低标准（Mode A · 罗生门后升级）

| 层 | 要求 |
| --- | --- |
| 片头 | 碎玻璃炸开 + 书卡（见 `opener.md`） |
| L1 主画面 | **2–3 静帧**（推荐中段加 1 张特写破幻灯片感）；相邻场 **不同** Ken Burns |
| L1b 段内 | 单场 ≥8s 时做 **两段** 运动（如 push → pan），禁止全程一个 from→to |
| L2 氛围 | 雾层漂移 + atmosphere 视差 |
| L3 环境 | **双层雨**（快/慢）+ 光尘；可加灯火呼吸 |
| 场切 | **0.5–0.6s opacity 叠化**，禁止硬切跳切 |

**不要**：为「动效多」硬切 8 场；也不要 2 图各一次微 zoom 像轮播。  
**要**：雨雾一直在动；镜头路径有变化；叠化衔接。

参考：`luoshengmen-video` 正片三场（全景 push/pan → 特写 settle → 人影 lift/drift）。

## Mode B：多场景时加强

| 层 | 作用 |
| --- | --- |
| L1 主画面 | Ken Burns：`push` / `pan-left` / `pan-right` / `lift` / `drift` / `settle` **相邻不重复** |
| L2 氛围 | `.atmosphere` 视差 |
| L3 环境 | 雨、烛光 flicker 按语义 |

可选：2+ 场视频背景（语义匹配时）。

## Ken Burns 参数参考

```js
const photoMotion = {
  push:    { from: { scale: 1.03, x: 0, y: 0 }, to: { scale: 1.12, x: 0, y: -10 } },
  "pan-left":  { from: { scale: 1.1, x: 20, y: 0 }, to: { scale: 1.1, x: -22, y: -4 } },
  "pan-right": { from: { scale: 1.1, x: -20, y: -3 }, to: { scale: 1.1, x: 22, y: 4 } },
  lift:    { from: { scale: 1.08, x: 0, y: 18 }, to: { scale: 1.12, x: 0, y: -20 } },
  drift:   { from: { scale: 1.09, x: -16, y: 10, rotation: -0.3 }, to: { scale: 1.12, x: 18, y: -8, rotation: 0.3 } },
  settle:  { from: { scale: 1.14, x: -8, y: -6 }, to: { scale: 1.06, x: 10, y: 6 } },
};
```

## 粒子层提示

- 雨：半透明竖线或小点下落，opacity 低，不挡字幕区  
- 落叶：大颗粒慢飘（对标病隙/雨街）  
- 光尘：微小点缓慢上浮  

Seek-safe：CSS infinite 或 GSAP 绑定主时间轴。

## 禁止

- 全片只有 scale 1.0→1.05 的微 zoom  
- 快速 shake / 炫光转场（除非片头）  
- 字幕 fade/blur 与口播抢同步（调试期硬切）  
