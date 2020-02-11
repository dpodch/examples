#include <iostream>
#include <cmath>

using namespace std;


float calcHeight(float timeInMs, float initialHeight)
{
	static const float g = 9.8;
	return initialHeight - g * pow(timeInMs / 1000, 2) / 2;
}

float getHeight()
{
	float height = 0;
	cout << "Please enter the height of a building in meteres: " << endl;
	cin >> height;
	return height;
}

float getNextTimeMs(float timeMs, float stepMs, float initialHeight, float &newHeight)
{
	float newTimeMs = timeMs + stepMs;

	newHeight = calcHeight(newTimeMs, initialHeight);

	if (newHeight < 0)
	{
		float height = calcHeight(timeMs, initialHeight);
		float k = height / (height - newHeight);

		newHeight = 0;
		newTimeMs = timeMs + stepMs * k;
	}
	return newTimeMs;
}

void print(float timeMs, float height)
{
	int sec = timeMs / 1000;
	int ms = timeMs - (sec * 1000);
	cout << "At";
	if (sec > 0)
	{
		cout << " " << sec << " sec";
	}

	if (ms > 0)
	{
		cout << " " << ms << " ms";
	}
	cout <<", the ball is at the height: " << height << " meteres" << endl;
}

int main() 
{
	const float initialHeight = getHeight();
	
	float timeInMs = 0;
	float timeStepMs = 1000;
	while (initialHeight >= 0)
	{
		float newHeight = 0;
		float newTimeMs = getNextTimeMs(timeInMs, timeStepMs, initialHeight, newHeight);
		print(newTimeMs, newHeight);

		if (newHeight <= 0)
		{
			break;
		}

		timeInMs = newTimeMs;
	}

	return 0;
}
