"""
纯Python五子棋游戏
使用说明：
1. 直接运行 python gomoku.py
2. 输入落子坐标，如"7,7"表示第8行第8列
3. 输入'quit'退出游戏
4. 输入'restart'重新开始
"""

class Gomoku:
    def __init__(self):
        self.reset_game()
    
    def reset_game(self):
        """重置游戏状态"""
        self.board = [['.' for _ in range(15)] for _ in range(15)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
    
    def print_board(self):
        """打印当前棋盘状态"""
        print("   " + " ".join(f"{i:2}" for i in range(15)))
        for i, row in enumerate(self.board):
            print(f"{i:2} " + " ".join(f"{cell:2}" for cell in row))
    
    def make_move(self, row, col):
        """
        玩家落子
        :param row: 行号(0-14)
        :param col: 列号(0-14)
        :return: (success, message) 元组
        """
        if self.game_over:
            return False, "游戏已结束，请重新开始"
        
        if not (0 <= row < 15 and 0 <= col < 15):
            return False, "坐标超出范围"
        
        if self.board[row][col] != '.':
            return False, "该位置已有棋子"
        
        self.board[row][col] = self.current_player
        
        if self.check_winner(row, col):
            self.game_over = True
            self.winner = self.current_player
            return True, f"玩家 {self.current_player} 获胜！"
        
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        return True, None
    
    def check_winner(self, row, col):
        """
        检查是否有玩家获胜
        :param row: 最后落子的行号
        :param col: 最后落子的列号
        :return: 是否获胜
        """
        directions = [
            [(0, 1), (0, -1)],  # 水平
            [(1, 0), (-1, 0)],  # 垂直
            [(1, 1), (-1, -1)],  # 主对角线
            [(1, -1), (-1, 1)]   # 副对角线
        ]
        
        player = self.board[row][col]
        
        for direction_pair in directions:
            count = 1
            for dx, dy in direction_pair:
                x, y = row + dx, col + dy
                while 0 <= x < 15 and 0 <= y < 15 and self.board[x][y] == player:
                    count += 1
                    x += dx
                    y += dy
            if count >= 5:
                return True
        return False

def main():
    """主游戏循环"""
    game = Gomoku()
    print("五子棋游戏开始！")
    print("输入坐标格式：行,列 (如 7,7)")
    print("输入'restart'重新开始，'quit'退出")
    
    while True:
        game.print_board()
        print(f"当前玩家: {game.current_player}")
        
        user_input = input("请输入落子坐标: ").strip()
        
        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'restart':
            game.reset_game()
            print("游戏已重置")
            continue
        
        try:
            row, col = map(int, user_input.split(','))
            success, message = game.make_move(row, col)
            if message:
                print(message)
                if game.game_over:
                    game.print_board()
                    if input("再玩一局？(y/n): ").lower() == 'y':
                        game.reset_game()
                    else:
                        break
        except ValueError:
            print("输入格式错误，请使用'行,列'格式")

if __name__ == "__main__":
    main()


