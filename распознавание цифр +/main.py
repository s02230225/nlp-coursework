if __name__ == "__main__":
    # распознавание цифр
    from tensorflow.keras.datasets import mnist
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.widgets as widgets
    from tensorflow import keras
    from tensorflow.keras.layers import Dense

    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    '''
    plt.figure(figsize=(10,5))
    for i in range(25):
        plt.subplot(5,5,i+1)
        plt.xticks([])
        plt.yticks([])
        plt.imshow(x_train[100+i], cmap=plt.cm.binary)
    plt.show()
    '''
    model = keras.Sequential([
        keras.layers.Flatten (input_shape=(28, 28, 1)),
        Dense(100, activation='relu'),
        Dense(10, activation='softmax')])
    '''print(model.summary())'''
    x_train = x_train / 255
    x_test = x_test / 255
    y_train_cat = keras.utils.to_categorical(y_train, 10)
    y_test_cat = keras.utils.to_categorical(y_test, 10)
    model.compile(optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy'])
    model.fit(x_train, y_train_cat, batch_size=32, epochs=10, validation_split=0.2,  verbose=False) #обучение
    print('*******   loss и accuracy  на тестовом наборе   ***********')
    model.evaluate(x_test, y_test_cat)
    print('*********    *****************')
    print ('проверка правильности некоторой цифры')
    n = 5
    x = np.expand_dims(x_test[n], axis=0)

    res = model.predict(x)
    print ('печать выходного вектора для', y_test[n])
    print( res )
    print
    print( np.argmax(res) , '  - такая цифра должна быть на рисунке. Верно?')
    plt.imshow(x_test[n], cmap=plt.cm.binary)
    plt.show()

    pred = model.predict(x_test)
    pred = np.argmax(pred, axis=1)
    '''
    print('вывод некоторых ошибочных некоторых результатов')
    print('смотрим, правильные ли ошибочные картинки, хорошо ли нарисованы')
    '''
    er=0
    for i in range(10000):
         if pred[i]!=y_test[i]:
             er=er+1
             '''
             if er>10 and er<16:
                 print("Значение сети: ", y_test[i], ' предсказано   ', pred[i] )
                 plt.imshow(x_test[i], cmap=plt.cm.binary)
                 plt.show()
             '''
            
    print ('k-vo  error ', er)

    # =============================================================================

    # =============================================================================
    # ИСПРАВЛЕННАЯ РИСОВАЛКА БЕЗ ИНВЕРСИИ
    # =============================================================================

    class DigitDrawer:
        def __init__(self):
            self.fig, self.ax = plt.subplots(figsize=(6, 6))
            self.ax.set_title('Рисуйте цифру (зажимайте левую кнопку мыши)')
            self.ax.set_xlim(0, 28)
            self.ax.set_ylim(0, 28)
            self.ax.invert_yaxis()
            
            self.canvas = np.zeros((28, 28))
            self.img = self.ax.imshow(self.canvas, cmap=plt.cm.binary, vmin=0, vmax=1)
            
            self.fig.canvas.mpl_connect('button_press_event', self.on_press)
            self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
            self.fig.canvas.mpl_connect('button_release_event', self.on_release)

            self.ax_recognize = plt.axes([0.7, 0.02, 0.2, 0.06])
            self.ax_clear = plt.axes([0.4, 0.02, 0.2, 0.06])
            self.btn_recognize = widgets.Button(self.ax_recognize, 'Распознать')
            self.btn_clear = widgets.Button(self.ax_clear, 'Очистить')
            
            self.btn_recognize.on_clicked(self.recognize_digit)
            self.btn_clear.on_clicked(self.clear_canvas)
            
            self.drawing = False
            self.last_point = None
            
        def on_press(self, event):
            if event.inaxes == self.ax:
                self.drawing = True
                self.draw_point(event)
        
        def on_motion(self, event):
            if self.drawing and event.inaxes == self.ax:
                self.draw_line(event)
        
        def on_release(self, event):
            self.drawing = False
            self.last_point = None
        
        def draw_point(self, event):
            x = int(event.xdata)
            y = int(event.ydata)
            
            if 0 <= x < 28 and 0 <= y < 28:
                self.canvas[y, x] = 1.0
            
            self.last_point = (x, y)
            self.img.set_array(self.canvas)
            self.fig.canvas.draw()
        
        def draw_line(self, event):
            x = int(event.xdata)
            y = int(event.ydata)
            
            if self.last_point and 0 <= x < 28 and 0 <= y < 28:
                x1, y1 = self.last_point
                points = self.get_line_points(x1, y1, x, y)
                for px, py in points:
                    if 0 <= px < 28 and 0 <= py < 28:
                        self.canvas[py, px] = 1.0
            
            self.last_point = (x, y)
            self.img.set_array(self.canvas)
            self.fig.canvas.draw()
        
        def get_line_points(self, x1, y1, x2, y2):
            points = []
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            sx = 1 if x1 < x2 else -1
            sy = 1 if y1 < y2 else -1
            err = dx - dy
            
            while True:
                points.append((x1, y1))
                if x1 == x2 and y1 == y2:
                    break
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x1 += sx
                if e2 < dx:
                    err += dx
                    y1 += sy
            return points
        
        def clear_canvas(self, event=None):
            self.canvas = np.zeros((28, 28))
            self.img.set_array(self.canvas)
            self.fig.canvas.draw()
            print("Холст очищен")
        
        def recognize_digit(self, event=None):
            input_image = self.canvas.reshape(1, 28, 28)
            
            prediction = model.predict(input_image, verbose=0)
            predicted_digit = np.argmax(prediction)
            confidence = np.max(prediction)
            
            print(f"\n=== РАСПОЗНАВАНИЕ ===")
            print(f"Сеть предсказала: {predicted_digit}")
            print(f"Уверенность: {confidence:.4f}")
            
            top3 = np.argsort(prediction[0])[-3:][::-1]
            print("Топ-3 предсказания:")
            for i, digit in enumerate(top3):
                print(f"  {i+1}. Цифра {digit}: {prediction[0][digit]:.4f}")
            
            plt.figure(figsize=(8, 4))
            plt.subplot(1, 2, 1)
            plt.imshow(self.canvas, cmap=plt.cm.binary)
            plt.title('Ваш рисунок')
            plt.subplot(1, 2, 2)
            plt.imshow(input_image[0], cmap=plt.cm.binary)
            plt.title(f'Предсказано: {predicted_digit}')
            plt.show()

    print("\n" + "="*60)
    print("ЗАПУСК ПРИЛОЖЕНИЯ ДЛЯ РИСОВАНИЯ ЦИФР")
    print("="*60)


    drawer = DigitDrawer()
    plt.show()
