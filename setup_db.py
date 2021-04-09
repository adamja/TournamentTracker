from tournamenttracker import bcrypt, db, create_app


def check_db_created():
    """ Create a working app for first run with default data """
    app = create_app()

    with app.app_context():
        from tournamenttracker.models import Game
        try:
            if Game.query.all() is None:
                print('No games found, creating default game with dummy tournament.')
                create_default_games()
                create_dummy_tournament()
        except Exception as e:
            print('No database found, creating one now...')
            create_db()
            print('Creating default game with dummy tournament.')
            create_default_games()
            create_dummy_tournament()


def create_db():
    """ Create the database based on the models.py configuration """
    app = create_app()

    with app.app_context():
        db.create_all()


def create_default_games():
    """ Add default games to the app """
    app = create_app()

    with app.app_context():
        from tournamenttracker.models import Game
        db.session.add(Game(name='Heroes Of Newerth', image_file='heroes-of-newerth_logo.png'))
        # db.session.add(Game(name='Dota2', image_file='dota-2_logo.jpg'))
        # db.session.add(Game(name='Super Smash Brothers', image_file='ssb_logo.png'))
        # db.session.add(Game(name='War Machine', image_file='warmahordes_logo.png'))
        db.session.commit()


def create_dummy_tournament():
    """ Create a dummy tournament to show app working for first run """
    app = create_app()

    with app.app_context():
        from tournamenttracker.models import BalanceMode, Game, Tournament, Player, Match, MatchPlayer, User

        # Create a user
        hashed_password = bcrypt.generate_password_hash('pw1234').decode('utf-8')
        user = User(username='admin', email='admin@gmail.com', password=hashed_password)
        db.session.add(user)

        # Find the game
        game = Game.query.filter_by(name="Heroes Of Newerth").first()
        db.session.add(game)

        # Create the tournament
        tournament = Tournament(name='HoN Night 1', user_id=user.id, game_id=game.id)
        db.session.add(tournament)
        db.session.commit()

        # Create balance modes
        db.session.add(BalanceMode(name='Staggered', sequence='1,3,5,7,9,2,4,6,8,10', description='Staggered'))
        db.session.add(BalanceMode(name='First With Last', sequence='1,4,5,7,10,2,3,6,8,9', description='First With Last'))
        db.session.add(BalanceMode(name='Chunking', sequence='1,5,6,7,10,2,3,4,8,9', description='Chunking'))
        db.session.add(BalanceMode(name='Auto Balance', sequence='', description='Auto Balance'))
        db.session.commit()

        # Add players to the tournament
        players = [
            Player(name='Adam', game_name='Bubs', tournament_id=tournament.id, start_points=10, image_file='ninja_bubbles.jpg'),
            Player(name='Matt', game_name='Pesti', tournament_id=tournament.id, start_points=9, image_file='pestilence.jpg'),
            Player(name='John', game_name='CD', tournament_id=tournament.id, start_points=8, image_file='cd.jpg'),
            Player(name='Val', game_name='Hag', tournament_id=tournament.id, start_points=7, image_file='wretched_hag.jpg'),
            Player(name='Barkley', game_name='Bomb', tournament_id=tournament.id, start_points=6, image_file='bombardier.jpg'),
            Player(name='Nick', game_name='Emp', tournament_id=tournament.id, start_points=5, image_file='empath.jpg'),
            Player(name='Andy', game_name='Geo', tournament_id=tournament.id, start_points=4, image_file='geomancer.jpg'),
            Player(name='Tom', game_name='Myrm', tournament_id=tournament.id, start_points=3, image_file='myrmidon.jpg'),
            Player(name='Liam', game_name='Dev', tournament_id=tournament.id, start_points=2, image_file='devourer.jpg'),
            Player(name='Angelo', game_name='Rav', tournament_id=tournament.id, start_points=1, image_file='ravenor.jpg'),
            ]

        for player in players:
            db.session.add(player)

        db.session.commit()

        # Create a match
        bm = BalanceMode.query.filter_by(name="Staggered").first()
        match = Match(name='Match 1', balance_mode_id=bm.id, tournament_id=tournament.id)
        db.session.add(match)

        db.session.commit()

        # Create a match player
        for player in players:
            db.session.add(MatchPlayer(match_id=match.id, player_id=player.id))

        db.session.commit()