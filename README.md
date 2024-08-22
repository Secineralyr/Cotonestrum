# Cotonestrum

コトネストルム

ねむすぎー用絵文字モデレーションツールです。起動にはRecipiens Cotonestrumが起動していないと動作しません。

## 開発用環境構築方法

### step1: venvを作成する

```
python -m venv .venv
```

作成後、各環境に合わせてアクティベートを行ってください。

### step2: ライブラリをインストールする

```
python -m pip install -U pip
python -m pip install -r requirements.txt
```

### step3: 起動する

複数存在します。

```
flet run src/main.py
or
python src/main.py
```

起動したら初期設定を行ってください。

### PyInstallerのビルド方法

```
python bundle.py
```

成功するとbinディレクトリ内にビルドされた実行ファイルが生成されます。

### fletでのビルド方法

基本使用されません。

```
flet build
```
