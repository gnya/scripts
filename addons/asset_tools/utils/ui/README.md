## これは何？

UIを描画する際にすこし便利なユーティリティです

## 使い方

使い方を簡単に説明します

> **注意**　これは `0.2.0` 時点の使用方法であり、今後の更新で変更される可能性があります

まずこのモジュールをインポートします

``` python
from asset_tools import utils
```

つぎにUIのレイアウトを次のような構造の辞書型の変数で定義します

```
{
    <data path> or $<operator id>: {
        <property id>: (<group name>, <text>, <icon>, <order>, <width>)
    }
}
```

以下にUIのレイアウト定義の例を示します

``` python
UI_CONTENTS = {
    'data.path.sample0': {
        'prop0': ('Sample0', 'Property 0', 'HIDE_OFF', 0, 1.0),
        'prop1[0]': ('Sample0', 'Property 1 L', '', 1, 0.5),
        'prop1[1]': ('Sample0', 'Property 1 R', '', 2, 0.5),
    },
    'data.path.sample1': {
        '["sample_prop"]': ('Sample1', 'Custom Property', '', 100, 1.0),
    }
    '$sample.sample_operator': {
        'type': ('Sample0', 'Button', '', 200, 1.0)
    }
    '$sample.sample_operator': {
        '': ('Sample1', 'Enum Dropdown', '', 200, 1.0)
    }
}
```

さいごに、UIの描画を行う例を以下に示します

``` python
        contents = {}
        utils.ui.collect_contents(contents, obj, UI_CONTENTS)
        utils.ui.collect_contents(contents, None, OTHER_UI_CONTENTS)

        col = self.layout.column(align=True)
        utils.ui.draw_contents(col, contents)
```
