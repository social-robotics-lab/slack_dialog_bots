import json

class ScenarioManager(object):
    def __init__(self, scenario:dict):
        self._scn = scenario
        self._gen = self._response_gen(scenario["MAIN"])
        self._is_initialized = False

    def next(self, user_input=None):
        if not self._is_initialized:
            self._is_initialized = True
            return next(self._gen)
        return self._gen.send(user_input)

    def _response_gen(self, dialog):
        for behavior in dialog:
            while True:
                user_input = yield behavior
                
                if behavior["type"] == "wait" and user_input:
                    # 現在のビヘイビアがwaitかつユーザからの入力の場合、マッチするシナリオの一つめのビヘイビアを返す
                    branch_label = behavior["branch"]
                    scn_options = self._scn[branch_label]
                    scn = self._select_scn(scn_options, user_input)
                    # TODO: 再帰でどうやってsendするか？
                    gen = self._response_gen(scn["dialog"])
                    user_input = yield next(gen)
                    try:
                        while True:
                            user_input = yield gen.send(user_input)
                    except StopIteration:
                        break
                if behavior["type"] == "wait" and not user_input:
                    # 現在のビヘイビアがwaitかつユーザからの入力でない場合、現在のビヘイビアを返す
                    continue
                if behavior["type"] != "wait" and user_input:
                    # 現在のビヘイビアがwait以外かつユーザからの入力の場合、現在のビヘイビアを返す
                    continue
                if behavior["type"] != "wait" and not user_input:
                    # 現在のビヘイビアがwait以外かつユーザからの入力でない場合、次のビヘイビアを返す
                    break

    def _select_scn(self, scn_options, text):
        for scn in scn_options:
            if scn["pattern"] == "*":
                return scn
            if scn["pattern"] in text:
                return scn
        return {}



if __name__ == "__main__":
    f = open("scenario.json", "r", encoding="utf-8")
    scenario = json.load(f)
    f.close()
    sm = ScenarioManager(scenario)
    behavior = sm.next()
    print(behavior)
    past_behavior = behavior
    try:
        while True:
            user_input = input("> ")
            behavior = sm.next(user_input)
            if behavior == past_behavior: continue
            print(behavior)
            past_behavior = behavior
    except StopIteration:
        print("終了")