import random, math

def getMeasurement(value=100, error=10):
    # return (value - (2 * error * random.random() - error), error)
    return (value + error * math.sin(random.random() * math.pi), error)
    
def RealTimeFilter(until=100, reset=8, eestReset=200):
	est_ = 0
	eest_ = 1000
	for i in range(until):
		measurement, measurementError = getMeasurement(100 - 90 * math.sin(i * 0.04), 10)

		if i % reset == 0:
			eest_ = eestReset
		
		kg = eest_ / (eest_ + measurementError)
		est = est_ + kg * (measurement - est_)
		eest = (1 - kg) * eest_

		error = 100 * abs(measurement - est) / measurement

		print('measurement: {0:.2f} \t estimation: {1:.2f} \t error: {2:.2f}'.format(measurement, est, error))

		eest_ = eest
		est_ = est
