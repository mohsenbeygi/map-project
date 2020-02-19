#include <bits/stdc++.h>
using namespace std;


int main()
{

    int num1, num2, num3;
    stringstream ss;
    string line;

    ifstream myfile ("graph_data.txt");

    if (myfile.is_open())
    {

        while ( getline (myfile, line) )
        {

            stringstream ss;
            ss << line;
            ss >> num1 >> num2 >> num3;
            cout << "nums: " << num1 << ", " << num2 << ", " << num3 << "\n";

        }

    myfile.close();

    }

    else cout << "Unable to open file";

    return 0;
}
