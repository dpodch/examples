#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

class EchoClass
{
    public:
        EchoClass(const std::string &msg)
        {
            cout << endl << "Created";
            this->msg = msg;
        }

        ~EchoClass()
        {
            cout << endl << "Deteled";
        }

        void echo()
        {
            cout << endl << msg;
        }

    private:
        std::string msg;
};

EchoClass* createClass(const std::string &msg)
{
    EchoClass *res = new EchoClass(msg);
    return res;
}

EchoClass createCopyClass(const std::string &msg)
{
    EchoClass res(msg);
    return res;
}

int main()
{
    // тут будет создан объект в рамках функции createClass. И у этого объекта будет вызван echo в рамказ функции main. Потом этот объект будет уничтожен черех delete
    // Теоретически объеект echoObject можно сразу не удалять, а использовать его где-то в другом месте, хранить его. Это не будет глобальной меременной и к нему доступ будет иметь только тот, кому ты его передаешь в качестве входных парметров
    cout << endl << "Begin heap pointer example";
    auto echoObject = createClass("Hello heap Alsu!!!");
    echoObject->echo();
    delete echoObject;
    cout << endl << "End heap pointer example";

     // тут будет создан объект, передана в main его копия. Получаетя избыточное копирование (если таких операций много или объект очень большой или объект хранит состояние, то это вызовет большие проблемы)ю Удалится объект, когда закончится его область видимости, т.е. main
    cout << endl << "Begin stack example";
    auto echoObject1 = createCopyClass("Hello stack Alsu!!!");
    echoObject1.echo();
    cout << endl << "End stack example";

    cout << endl << "End main";
    return 0;
}