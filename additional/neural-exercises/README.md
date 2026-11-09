# Нейросетевые упражнения

Персептрон, XOR, чётность, линейная зависимость и обучение с Dropout на MNIST.

| Файл | Назначение |
| --- | --- |
| [linear_relation.py](linear_relation.py) | Программа или модуль практикума |
| [perceptron.py](perceptron.py) | Программа или модуль практикума |
| [perceptron_training.py](perceptron_training.py) | Программа или модуль практикума |
| [xor_training.py](xor_training.py) | Программа или модуль практикума |
| [xor_network.py](xor_network.py) | Программа или модуль практикума |
| [parity_network.py](parity_network.py) | Программа или модуль практикума |
| [mnist_dropout.ipynb](mnist_dropout.ipynb) | Ноутбук с постановкой, реализацией и анализом |

Зависимости устанавливаются для выбранной работы отдельно:

```bash
python3 -m pip install -r requirements.txt
```

Ноутбуки открываются в Jupyter; ячейки выполняются последовательно. Скрипты запускаются из этой папки. Необходимые входные файлы и ресурсы перечислены в [INPUTS.md](INPUTS.md).

Загрузчики датасетов могут обращаться к сети при отсутствии локального кеша.
