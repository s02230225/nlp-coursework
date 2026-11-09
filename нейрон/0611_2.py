if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt
    from tensorflow import keras
    from tensorflow.keras.layers import Dense

    #################################################################################################
    A = 0.001
    B = -0.001
    def myf(x):
        return (A*x+B)
    c = np.array([-1, 1]) 
    Ep = 100
    ################################################################################################

    f = np.array([myf(i) for i in c])
    model = keras.Sequential()
    model.add(Dense(units=1, input_shape=(1,), activation='linear'))
    print ('модель построена')
    model.summary()
    model.compile(loss='mean_squared_error', optimizer=keras.optimizers.Adam(0.1))
    log = model.fit(c, f, epochs=Ep, verbose=False)
    plt.plot(log.history['loss'])
    plt.grid(True)
    plt.show()
    print('f(2)=',model.predict(np.array([2])))
    print('f(-10)=',model.predict(np.array([-10])))
    print('f(10)=',model.predict(np.array([10])))
    print('веса  ', model.get_weights())
