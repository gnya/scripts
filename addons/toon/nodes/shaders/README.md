## これはなに？
[Open Shader Language](https://docs.blender.org/manual/en/latest/render/shader_nodes/osl.html) (OSL) で記述された個人プロジェクト用のシェーダースクリプトです<br>

> [!NOTE]
> Blender 3.6.0 の Cycles でスクリプトノードから読み込んで使用することを想定しています

## 各スクリプトの説明

### `area_light.osl`

#### Inputs
* Location

  ライトオブジェクトの位置（ワールド座標系）

* Rotation

  ライトオブジェクトのオイラーXYZ回転角（ワールド座標系）

* Energy

  ライトオブジェクトの光源の強さ

* Distance

  光源の強さが1/2に減衰する距離

#### Outputs
* Light

  レンダリングポイントにおけるライトベクトル

### `sun_light.osl`

#### Inputs
* Rotation

  ライトオブジェクトのオイラーXYZ回転角（ワールド座標系）

* Energy

  ライトオブジェクトの光源の強さ

#### Outputs
* Light

  レンダリングポイントにおけるライトベクトル

### `point_light.osl`

#### Inputs
* Location

  ライトオブジェクトの位置（ワールド座標系）

* Energy

  ライトオブジェクトの光源の強さ

* Distance

  光源の強さが1/2に減衰する距離

#### Outputs
* Light

  レンダリングポイントにおけるライトベクトル

### `tex_light.osl`

#### Inputs
* Location

  ライトオブジェクトの位置（ワールド座標系）

* Rotation

  ライトオブジェクトのオイラーXYZ回転角（ワールド座標系）

* Energy

  ライトオブジェクトの光源の強さ

* Size

  ライトに照らされる領域の大きさを表す角度

#### Outputs
* Light

  レンダリングポイントにおけるライトベクトル

* UV

  レンダリングポイントにおけるライトテクスチャのUV座標

### `material.osl`

#### Inputs
* Light

  レンダリングポイントにおけるライトベクトル

* Cutoff

  影の境界に出るギザギザを調整するためのパラメータ

* Reflectance

  スペキュラーの反射率

* Exponent

  スペキュラーの指数

#### Outputs
* IsCycles

  現在のレンダラーにCyclesが使用されているかどうか

* Diffuse

  ディフューズの値

* Specular

  スペキュラーの値

### `to_closure.osl`

#### Inputs
* Color

  色

* Reflectance

  光沢の強さ

* Distance

  光沢の最大距離

* Depth

  光沢を計算する際の反射回数の上限

* Transparency

  透明度

#### Outputs
* Shader

  シェーダー

### `matcap.osl`

#### Outputs
* UV

  レンダリングポイントにおけるMatcapのUV座標

### `visualize.osl`

#### Inputs
* Type

  ビジュアライズするプロパティの種類

  | Type | 説明 |
  | :-: | :-: |
  | 0 | 影のグループID |
  | 1 | 透過のグループID |
  | 2 | 影のプロパティ |

#### Outputs
* Color

  プロパティの値によって色分けされた結果

### `uv_pixel_snap.osl`

#### Inputs
* UV

  元のUV

* Width

  幅方向の解像度

* Height

  高さ方向の解像度

#### Outputs
* UV

  離散化されたUV

### `hsv_jitter.osl`

#### Inputs
* Seed

  乱数のシード値

* Hue Jitter

  色相の振れ幅

* Saturation Jitter

  彩度の振れ幅

* Value Jitter

  明度の振れ幅

* Fac Jitter

  係数の振れ幅

* Hue

  色相

* Saturation

  彩度

* Value

  明度

* Fac

  係数

#### Outputs
* Hue

  色相

* Saturation

  彩度

* Value

  明度

* Fac

  係数

## プロパティ
オブジェクトインデックスとマテリアルインデックスに設定する値によって<br>
影や透過などの処理を行う際の挙動を設定することができます

|  | 5桁目 | 3-4桁目 | 1-2桁目 |
| :-: | :-: | :-: | :-: |
| 機能 | 影の投影 | 透過のグループID | 影のグループID |
| 値の範囲 | `0` - `2` | `0` - `63` |`0` - `63` |
| 初期値 | `0` | `0` | `0` |

オブジェクトとマテリアルで値が競合する場合は前者が優先されます

### 影のグループID
グループのIDは `1` から `63` までの数字で `0` の場合は何もしません

同じグループのIDに設定されたもの同士は影を落としません<br>
グループのIDを設定されたオブジェクトが自身に落とす影も無効になります

### 影の投影
他のオブジェクトに対してどのように影を落とすかを設定します

| 値 | 影の投影の挙動 |
| :-: | :-: |
| `0` | 影を落とす |
| `1` | 表面のみに影を落とす |
| `2` | 影を落とさない |

### 透過のグループID
グループのIDは `1` から `63` までの数字で `0` の場合は何もしません

同じグループのIDに設定されたもの同士は互いに重なって描画されません<br>
別のグループのIDに設定されたもの同士とは重なって描画されます