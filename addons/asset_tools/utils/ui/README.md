## これは何？

UIを描画する際にすこし便利なユーティリティです

## 使い方

使い方を簡単に説明します

> [!NOTE]
> これは `0.2.2` 時点の使用方法であり、今後の更新で変更される可能性があります

まずこのモジュールをインポートします

``` python
from asset_tools import utils
```

つぎにUIのレイアウトを次のような構造の辞書型の変数で定義します

```
{
    <group name>: {
        <data path> or <operator id>: (<text>, <icon>, <order>, <width>)
    }
}
```

以下にUIのレイアウト定義の例を示します

``` python
UI_CONTENTS = {
    'Sample0': {
        'data.path.sample0': {
            'prop0': ('Property 0', 'HIDE_OFF', 0, 1.0),
            'prop1[0]': ('Property 1 L', '', 1, 0.5),
            'prop1[1]': ('Property 1 R', '', 2, 0.5)
        },
        '$sample.sample_operator': {
            'type': ('Enum Dropdown', '', 3, 1.0),
            'sample_arg0': 'Test0'
        }
    },
    'Sample1' {
        'data.path.sample1': {
            '["sample_prop"]': ('Custom Property', '', 0, 1.0)
        },
        '$sample.sample_operator': ('Button', '', 1, 1.0)
    }
}
```

さいごに、UIの描画を行う例を以下に示します

``` python
col = self.layout.column(align=True)

# 定義したレイアウト UI_CONTENTS_0 を描画する
utils.ui.draw(col, UI_CONTENTS_0, obj)

# データパスがフルパスの場合はdataを省略できます
utils.ui.draw(col, UI_CONTENTS_1)

# 可変長引数でオペレーターの引数を設定できます
utils.ui.draw(col, UI_CONTENTS_2, sample_arg1='Test1')

# レイアウト定義の引数にタプル型を渡すこともできます
utils.ui.draw(col, (UI_CONTENTS_3, UI_CONTENTS_4))
```
