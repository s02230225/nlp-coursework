if __name__ == "__main__":
    from numpy import exp, array, random, dot
    training_set_inputs = array([
        [1,0,0],  # → 1
        [0,0,1],  # → 0
        [0,1,0],  # → 1
        [0,1,1],  # → 1
    ])
    training_set_outputs = array([[1, 0, 1, 1]]).T
    weights =[[0.5], [0.5], [0.5]]
    x=10000
    for iteration in range(x):
         output = 1 / (1 + exp(-(dot(training_set_inputs, weights))))
         weights += dot(training_set_inputs.T, (training_set_outputs - output) * output * (1 - output))
         if iteration%(x/4)==0:
                 print (weights, '   ', 1 / (1 + exp(-(dot(array([0,1, 1]), weights)))))

    print ('x= ', x)
    print ('результат на обучающем наборе')
    print (output)

    new=[1,1,0]
    print ( 'предсказание для  ', new)
    print ( 1 / (1 + exp(-(dot(array(new), weights)))))
