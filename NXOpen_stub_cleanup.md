# NXOpen Stub 清洗说明

## 目标

这份说明记录当前 NXOpen stub 清洗策略，以及为什么要把大量成员声明转换成 `@property` 形式。

当前背景：

- 原始 NXOpen 生成文件更接近 .NET 风格导出，不是标准 Python stub。
- Pylance 能索引到部分符号，但在链式推断上经常断掉。
- 典型问题是 `NXOpen.Session.GetSession().ListingWindow.Open()` 这种链条里，前半段能找到名字，后半段却不能稳定推断类型和跳转。

## 为什么 `@property` 更稳

原始字段式声明通常长这样：

```python
ListingWindow: ListingWindow
```

对自动生成的 NXOpen stub 来说，这种写法对 Pylance 不够稳定。语言服务有时会把它当成“类里声明过一个名字”，但不一定稳定推断成“实例访问时返回这个类型”。

改成 property 之后，语义会更明确：

```python
@property
def ListingWindow(self) -> ListingWindow: ...

@ListingWindow.setter
def ListingWindow(self, value: ListingWindow) -> None: ...
```

这样做的好处：

- 明确告诉 Pylance：这是实例成员访问，不是普通类变量。
- 对链式表达式的返回类型更稳定。
- 悬停、补全、跳转到定义更容易命中。
- 增加 setter 后，不会把原本可能可写的成员强行变成只读。

这不是说所有 Python 代码都应该优先用 `@property`。这里只是因为 NXOpen 这批自动生成 stub 更像“对象属性 API”，而不是普通数据类字段。

## 当前清洗规则

清洗脚本位于 [scripts/clean_nxopen_stubs.py](scripts/clean_nxopen_stubs.py)。当前主要规则如下。

### 1. 清理不合法标识符

- 修正保留字和非法名字。
- 处理类似 `None`、`True`、`False` 被当成参数名或成员名的情况。
- 处理带点号或编译器产物的名字，例如 `Foo.Factory`、`<>c`。

### 2. 统一函数签名

- 把跨多行的生成签名压成单行 stub 风格。
- 吞掉函数体里的残留内容，比如文档字符串和孤立的 `...`。
- 对同名重复定义自动补 `@typing.overload`。
- 如果类内方法首参不是 `self` 或 `cls`，自动补 `@staticmethod`。

典型例子：

```python
@staticmethod
def GetSession() -> Session: ...
```

这对 `NXOpen.Session.GetSession()` 这种调用很关键。

### 3. 批量提升成员为 property

对非 `enum.Enum` 类中、类体第一层的简单类型注解成员：

```python
Name: SomeType
```

会转换为：

```python
@property
def Name(self) -> SomeType: ...

@Name.setter
def Name(self, value: SomeType) -> None: ...
```

当前会排除：

- `enum.Enum` 类中的成员
- `ClassVar[...]` 成员
- 不是简单注解行的内容

### 4. 修正常见坏注解

- 把 `any` 统一成 `typing.Any`
- 把 `typing.List[Tag[]]` 之类的残留形式修成合法 Python 类型注解

### 5. 处理空类和自导入

- 空类自动补 `...`
- 删除类似 `from ..NXOpen import *` 这类对 stubPath 不友好的自导入

## 为什么要保留 setter

如果只生成 getter：

```python
@property
def Scale(self) -> float: ...
```

那么 Pylance 往往会把它视为只读属性。

这对某些 NXOpen API 不一定准确，因为不少成员在实际语义上更像“可取可设的属性”。因此当前策略是默认生成 getter + setter：

```python
@property
def Scale(self) -> float: ...

@Scale.setter
def Scale(self, value: float) -> None: ...
```

这样对静态分析更稳，也更接近 .NET 属性的读写语义。

## 当前效果

这套规则已经用于当前 NXOpen stub 目录。针对最初的示例：

```python
listing_window = NXOpen.Session.GetSession().ListingWindow
listing_window.Open()
```

现在 Pylance 可以稳定解析：

- `GetSession` 返回 `Session`
- `ListingWindow` 返回 `ListingWindow`
- `Open()` 跳到对应 stub 定义

## 重跑方式

如果后续重新生成了 NXOpen 文件，可以重新运行：

```powershell
e:/NX_develop/project/.venv/Scripts/python.exe scripts/clean_nxopen_stubs.py "E:/NX_develop/20230921Intellisense/Release2023" "E:/NX_develop/20230921Intellisense/Release2023_clean"
```

如果确认输出没有问题，再覆盖原目录：

```powershell
Copy-Item -Path "E:\NX_develop\20230921Intellisense\Release2023_clean\*" -Destination "E:\NX_develop\20230921Intellisense\Release2023" -Recurse -Force
```

如果原目录里还留有旧 `.py`，建议删除，只保留 `.pyi`，避免 Pylance 混用旧文件。

## 已知取舍

当前策略偏向“让 Pylance 稳定工作”，不是严格还原原始生成器的全部语义。

具体取舍：

- 大量注解字段会被提升成 property，这更利于链式推断。
- 一些原本更像纯数据字段的成员，也会一起被 property 化。
- 但因为保留了 setter，这种改动通常不会影响静态分析层面的可写性判断。

如果后续发现某一类成员不适合 property 化，可以继续在清洗器里加排除规则，而不是回退到全字段模式。

## 建议

- 把清洗器当成 NXOpen 生成后的固定后处理步骤。
- 优先维护清洗规则，不要手工改大量生成文件。
- 每次大改规则后，都重新跑一遍全量编译验证。