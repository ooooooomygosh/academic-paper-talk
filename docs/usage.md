# 使用指南

## 最少输入

一篇全文 PDF，加一句“用 Academic Paper Talk 制作精读 PPT”。受众默认为有相关基础但没读过论文的研究生。未指定的时长和页数是可调整起点，不是必须完成的配额。

## 常用请求

```text
使用 $artifact-template-academic-paper-talk，做一份 15 分钟中文汇报。
请用一个样本走完算法，重点解释每次观测如何影响下一步。
```

```text
使用 $artifact-template-academic-paper-talk 修改已有 PPT。
总体图和模块图之间的关系没讲清，请重构方法页，保留实验原图。
```

```text
使用 $artifact-template-academic-paper-talk，总共 10 页，包含封面。
按我上传的导师模板排版，备注仍要可以直接朗读。
```

## 工作过程

agent 会读全文、核对关键图表，建立问题—机制—证据关系，再保存逐页大纲并继续制作。无需为默认配色或已经确定的篇幅重复确认。论文全文缺失、任务对象无法确定等会影响成品的缺口需要补充。

新论文的数据、变量、模块和结论不会从参考 deck 继承。新增教学例子要标明示例；原文没有披露的细节不会自动补成事实。

## 检查朗读稿

使用 `--script` 检查时，Markdown 每个二级标题对应一页，标题后的内容只保留该页口播：

```markdown
# 逐页朗读稿

## 第 1 页 论文与问题

本页的完整口播……

## 第 2 页 关键观察

本页的完整口播……
```

也可用 `--expected-notes notes.json`，JSON 内容为按页排序的字符串数组。两个输入选项互斥。匹配时忽略排版空白，保留其余字符。

## 更新和卸载

更新仓库后执行 `python3 scripts/install.py --force`，旧版会自动备份。若安装后修改过 skill，应先比较新版与个人修改。卸载时删除你安装的 `artifact-template-academic-paper-talk` 目录即可，仓库和用户的 PPT 不受影响。
