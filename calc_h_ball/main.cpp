#include <iostream>
#include <cmath>

using namespace std;


float calcHeight(float timeInSec, float initialHeight)
{
	static const float g = 9.8;
	return initialHeight - g * pow(timeInSec, 2) / 2;
}

float getHeight()
{
	float height = 0;
	cout << "Please enter the height of a building in meteres: " << endl;
	cin >> height;
	return height;
}

int main() 
{
	const float initialHeight = getHeight();
	float height = initialHeight;

	cout << "the ball is at the height: " << height << "meteres" << endl;
	
	int timeInSec = 0;
	while (height > 0)
	{
		timeInSec++;
		height = calcHeight(timeInSec, initialHeight);
		cout << "At " << timeInSec << "seconds, the ball is at the height: " << height << "meteres" << endl;
	}

	return 0;
}
