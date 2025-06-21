#include <iostream>
#include <map>
using namespace std;

void boj26123();

int main() {
    ios::sync_with_stdio(false); cin.tie(NULL); cout.tie(NULL);

    boj26123();

    return 0;
}

void boj26123() {
    map<int, long long, greater<int>> todo;
    int num, day;
    int temp;
    long long cnt = 0;

    cin >> num >> day;

    for (int i = 0; i < num; i++) {
        cin >> temp;
        if (todo.find(temp) != todo.end())
            todo[temp]++;
        else
            todo[temp] = 1;
    }

    for (auto i = todo.begin(); i != todo.end() && day > 0; i++) {
        if (i->first == 0)
            break;
        cnt += i->second;
        if (todo.find(i->first - 1) != todo.end())
            todo[i->first - 1] += i->second;
        else
            todo[i->first - 1] = i->second;
        day--;
    }

    cout << cnt;

    return;
}