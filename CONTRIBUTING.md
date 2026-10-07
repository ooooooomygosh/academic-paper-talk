# 贡献指南

欢迎提交可复现的生成问题、具体的科学解释缺口、安装兼容性问题和文档改进。

修改前请阅读 `skills/artifact-template-academic-paper-talk/SKILL.md`。保持原参考资产不变；若确需更换，请说明来源、权限、预览与风格差异。不要提交私人论文库、会话导出、账户信息、绝对本机路径或生成工作目录。

提交前运行：

```bash
python3 scripts/check_package.py
python3 -m unittest discover -s tests -v
```

涉及 PPT 的改动还需人工检查受影响的成品页面。结构测试通过不能代替视觉与科学核对。问题描述请附最小复现、预期与实际结果、相关工具版本；公开附件前自行移除私人材料。
