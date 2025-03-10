from calendar import c
from sqlalchemy import ForeignKey, create_engine, Column, Integer, String, Boolean, Date, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from scrape_box_score import main as scrape_box_score
import asyncio
from pprint import pprint
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
from datetime import datetime

Base = declarative_base()

class Schedule(Base):
    __tablename__ = 'schedule'
    game_id = Column(Integer, primary_key=True, autoincrement=True)
    opponent = Column(Text)
    date = Column(Date)
    datetime = Column(DateTime)
    home = Column(Boolean)
    win = Column(Boolean)
    claflin_score = Column(Integer)
    opponent_score = Column(Integer)
    opp_logo = Column(Text)
    box_score_link = Column(Text)
    def __repr__(self):
        return f"<Schedule(game_id={self.game_id}, opponent={self.opponent}, date={self.date}, datetime={self.datetime}, home={self.home}, win={self.win}, claflin_score={self.claflin_score}, opponent_score={self.opponent_score}, opp_logo={self.opp_logo}, box_score_link={self.box_score_link})>"

class Player(Base):
    __tablename__ = 'player'
    player_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text)
    position = Column(Text)
    jersey_number = Column(Text)
    height = Column(Text)
    image = Column(Text)
    class_ = Column("class", Text)  # 'class' is a reserved keyword in Python
    hometown = Column(Text)
    high_school = Column(Text)
    def __repr__(self):
        return f"<Player(player_id={self.player_id}, name={self.name}, position={self.position}, jersey_number={self.jersey_number}, height={self.height}, class_={self.class_}, hometown={self.hometown}, high_school={self.high_school})>"

class BoxScore(Base):
    __tablename__ = 'box_score'
    game_id = Column(Integer, primary_key=True)
    team_name = Column(Text, primary_key=True)
    player_number = Column(Integer, primary_key=True)
    player = Column(Text)
    gs = Column(Boolean)
    min = Column(Integer)
    fg = Column(Text)
    pt3 = Column(Text)
    ft = Column(Text)
    orb_drb = Column(Text)
    reb = Column(Integer)
    pf = Column(Integer)
    a = Column(Integer)
    trn = Column(Integer)
    blk = Column(Integer)
    stl = Column(Integer)
    pts = Column(Integer)
    
    
    def to_dict(self):
        """ Convert the BoxScore object to a dictionary """
        return {
            "game_id": self.game_id,
            "team_name": self.team_name,
            "player_number": self.player_number,
            "player": self.player,
            "gs": self.gs,
            "min": self.min,
            "fg": self.fg,
            "pt3": self.pt3,
            "ft": self.ft,
            "orb_drb": self.orb_drb,
            "reb": self.reb,
            "pf": self.pf,
            "a": self.a,
            "trn": self.trn,
            "blk": self.blk,
            "stl": self.stl,
            "pts": self.pts
        }
    
class Drill(Base):
    __tablename__ = 'drills'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    improves = Column(Text, nullable=False)  # Stored as JSON string
    description = Column(Text, nullable=False)
    sets_reps = Column(Text, nullable=False)
    variations = Column(Text, nullable=True)  # Stored as JSON string

    def to_dict(self):
        """ Convert the Drill object to a dictionary """
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "improves": json.loads(self.improves),
            "description": self.description,
            "sets_reps": self.sets_reps,
            "variations": json.loads(self.variations) if self.variations else []
        }
        
class Workout(Base):
    __tablename__ = 'workouts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    player = Column(String, nullable=False)  # Reference to the Player ID
    hour = Column(Integer, nullable=False)  # Start time of the drill
    drill = Column(Integer,ForeignKey(Drill.name), nullable=False)  # Reference to the Drill ID
    scheduled_date = Column(Date, nullable=False)  # Date of the workout

    def to_dict(self):
        """ Convert the Workout object to a dictionary """
        return {
            "id": self.id,
            "player": self.player,
            "hour": self.hour,
            "drill_name": self.drill,
            "scheduled_date": self.scheduled_date.isoformat()
        }
    # Example usage:    
    # player_name = "John Doe"
    # box_scores = get_box_scores_for_player(player_name)
    # for box_score in box_scores:
    #     print(f"Game Date: {box_score.game.date}, Points: {box_score.pts}, Rebounds: {box_score.reb}, Assists: {box_score.a}")
# Database connection
engine = create_engine('sqlite:///C:/Users/tr102/code/bbtracker/basketball_stats.db', pool_size=10)
Base.metadata.create_all(engine)
# Example JSON representing a workout to be inserted

# Create a configured "Session" class
Session = sessionmaker(bind=engine)
# session = Session()
def get_schedule_by_player(player_name, session=Session()):
    """
    Retrieve the workout schedule for a player by their name.
    Args:
        player_name (str): The name of the player to search for.
        session (Session, optional): The SQLAlchemy session to use for the query. Defaults to a new Session instance.
    Returns:
        list[dict] or None: A list of dictionaries representing the player's workout schedule if the player is found,
                            otherwise None.
    """
    
    player = session.query(Player).filter(Player.name.ilike(f"%{player_name}%")).first()
    if not player:
        return None
    schedule = session.query(Workout).filter(Workout.player == player.name).all()
    return [item.to_dict() for item in schedule]

def get_schedule_by_player_for_day(player_name, scheduled_date,hour, session=Session()):
    """
    Retrieve the workout schedule for a specific player on a given day and hour.
    Args:
        player_name (str): The name of the player to search for.
        scheduled_date (date): The date for which the schedule is being retrieved.
        hour (int): The hour of the day for which the schedule is being retrieved.
        session (Session, optional): The SQLAlchemy session to use for the query. Defaults to a new session.
    Returns:
        list: A list of dictionaries representing the workout schedule for the player at the specified date and hour.
                Returns None if the player is not found.
    """
    
    player = session.query(Player).filter(Player.name.ilike(f"%{player_name}%")).first()
    print(player)
    print(scheduled_date)
    print(hour)
    if not player:
        return None
    schedule = session.query(Workout).filter(Workout.player == player.name).where(Workout.scheduled_date <= scheduled_date).where(Workout.hour == hour).all()
    print(schedule)
    return [item.to_dict() for item in schedule]

def add_drill_to_player_schedule(player_name, drill, scheduled_date, hour, session=Session()):
    """
    Adds a drill to a player's schedule.
    Args:
        player_name (str): The name of the player to whom the drill will be added.
        drill (str): The name of the drill to be added.
        scheduled_date (str): The date when the drill is scheduled, in ISO format.
        hour (int): The hour of the day when the drill is scheduled.
        session (Session, optional): The SQLAlchemy session to use for the database operations. Defaults to a new session.
    Returns:
        dict: A dictionary representation of the newly created schedule if the player is found, otherwise None.
    """
    
    player = session.query(Player).filter(Player.name.ilike(f"%{player_name}%")).first()
    if not player:
        return None

    # Convert scheduled_date to a Python datetime object
    scheduled_date = datetime.fromisoformat(scheduled_date.replace("Z", "+00:00")).date()
    new_schedule = Workout(
        player=player.name,
        scheduled_date=scheduled_date,
        hour=hour,
        drill=drill
    )
    session.add(new_schedule)
    session.commit()
    return new_schedule.to_dict()


def remove_drill_from_player_schedule(player_name, drill, scheduled_date, hour, session=Session()):
    player = session.query(Player).filter(Player.name.ilike(f"%{player_name}%")).first()
    if not player:
        return None

    # Convert scheduled_date to a Python datetime object
    scheduled_date = datetime.fromisoformat(scheduled_date.replace("Z", "+00:00")).date()
    schedule_item = session.query(Workout).filter(
        Workout.player == player.name,
        Workout.drill == drill,
        Workout.scheduled_date == scheduled_date,
        Workout.hour == hour
    ).first()
    if not schedule_item:
        return None
    session.delete(schedule_item)
    session.commit()
    return schedule_item.to_dict()


def get_drills(session=Session()):
    drills = session.query(Drill).all()
    return [drill.to_dict() for drill in drills]

def get_drills_by_category(category, session=Session()):
    drills = session.query(Drill).filter(Drill.category.ilike(f"%{category}%")).all()
    return [drill.to_dict() for drill in drills]

def get_drill_by_name(drill_name, session=Session()):
    drill = session.query(Drill).filter(Drill.name.ilike(f"%{drill_name}%")).first()
    if drill:
        return drill.to_dict()
    return None

def get_box_score_by_player(player_name, session=Session()):
    return session.query(BoxScore).filter(BoxScore.player.ilike(f"%{player_name}%")).all()

def get_last_x_games(player_name, x=5, session=Session()):
    last_games = (
        session.query(BoxScore)
        .filter(BoxScore.player.ilike(f"%{player_name}%"))
        .order_by(BoxScore.game_id.desc())  # Latest games first
        .limit(x)
        .all()
    )
    result = [u.__dict__ for u in last_games]
    [u.pop('_sa_instance_state', None) for u in result ]
    return last_games
    
def get_rolling_averages(player_name, x=5, session=Session()):
    games = get_last_x_games(player_name, x)
    if not games:
        return None

    total_games = len(games)
    avg_stats = {
        "fg_pct": sum(int(g.fg.split('-')[0]) / int(g.fg.split('-')[1]) for g in games if int(g.fg.split('-')[1]) > 0) / total_games,
        "3p_pct": sum(int(g.pt3.split('-')[0]) / int(g.pt3.split('-')[1]) for g in games if int(g.pt3.split('-')[1]) > 0) / total_games,
        "ft_pct": sum(int(g.ft.split('-')[0]) / max(1, int(g.ft.split('-')[1])) for g in games) / total_games,  # Avoid division by zero
        "reb": sum(int(g.reb) for g in games) / total_games,
        "assists": sum(int(g.a) for g in games) / total_games,
        "turnovers": sum(int(g.trn) for g in games) / total_games,
        "points": sum(int(g.pts) for g in games) / total_games
    }
    return avg_stats

def get_player(player_name, session=Session()):
    player = session.query(Player).filter(Player.name.ilike(f"%{player_name}%")).first()
    if player:
        return {
            "name": player.name,
            "position": player.position,
            "jersey_number": player.jersey_number,
            "height": player.height,
            "image": player.image,
            "class_": player.class_,
            "hometown": player.hometown,
            "high_school": player.high_school
        }
    return None

def get_season_averages(player_name, session=Session()):
    games = get_box_score_by_player(player_name)
    if not games:
        return None

    total_games = len(games)
    avg_stats = {
        "fg_pct": round(sum(int(g.fg.split('-')[0]) / int(g.fg.split('-')[1]) for g in games if int(g.fg.split('-')[1]) > 0) / total_games * 100, 2),
        "3p_pct": round(sum(int(g.pt3.split('-')[0]) / int(g.pt3.split('-')[1]) for g in games if int(g.pt3.split('-')[1]) > 0) / total_games * 100, 2),
        "ft_pct": round(sum(int(g.ft.split('-')[0]) / max(1, int(g.ft.split('-')[1])) for g in games) / total_games * 100, 2),  
        "reb": round(sum(int(g.reb) for g in games) / total_games, 2),
        "assists": round(sum(int(g.a) for g in games) / total_games, 2),
        "turnovers": round(sum(int(g.trn) for g in games) / total_games, 2),
        "points": round(sum(int(g.pts) for g in games) / total_games, 2),
        "minutes": round(sum(int(g.min) for g in games) / total_games, 2),
        "offensive_rebounds": round(sum(int(g.orb_drb.split('-')[0]) for g in games) / total_games, 2),
        "defensive_rebounds": round(sum(int(g.orb_drb.split('-')[1]) for g in games) / total_games, 2),
        "personal_fouls": round(sum(int(g.pf) for g in games) / total_games, 2),
        "blocks": round(sum(int(g.blk) for g in games) / total_games, 2),
        "steals": round(sum(int(g.stl) for g in games) / total_games, 2)
    }
    return avg_stats
def get_best_scoring_game(player_name, session=Session()):
    return session.query(BoxScore).filter(BoxScore.player == player_name).order_by(BoxScore.pts.desc()).first()

def get_worst_scoring_game(player_name, session=Session()):
    return session.query(BoxScore).filter(BoxScore.player == player_name).order_by(BoxScore.pts.asc()).first()

def get_high_turnover_games(player_name, threshold=3, session=Session()):
    return session.query(BoxScore).filter(BoxScore.player == player_name, BoxScore.trn >= threshold).all()

def get_high_3pt_games(player_name, threshold=0.4, session=Session()):
    high_3pt_games = []
    all_games = session.query(BoxScore).filter(BoxScore.player == player_name).all()
    for game in all_games:
        if int(game.pt3.split('-')[1]) > 0:  # Ensure there were 3-point attempts
            three_pt_percentage = int(game.pt3.split('-')[0]) / int(game.pt3.split('-')[1])
            if three_pt_percentage >= threshold:
                high_3pt_games.append(game)
    return high_3pt_games
    
def generate_training_recommendations(player_name):
    stats = get_season_averages(player_name)
    if not stats:
        return "No data available for training recommendations."

    recommendations = []

    # Shooting Training
    if stats["fg_pct"] < 0.45:
        recommendations.append("Improve shooting mechanics with form-focused drills and spot-up shooting.")

    if stats["3p_pct"] < 0.35:
        recommendations.append("Work on three-point consistency with catch-and-shoot drills.")

    if stats["ft_pct"] < 0.75:
        recommendations.append("Increase free throw efficiency with routine-based practice.")

    # Ball Handling & Playmaking
    if stats["turnovers"] > 3:
        recommendations.append("Reduce turnovers by improving ball control and decision-making.")

    if stats["assists"] < 3:
        recommendations.append("Enhance playmaking skills with pick-and-roll drills and passing vision work.")

    # Rebounding & Defense
    if stats["reb"] < 4:
        recommendations.append("Increase rebounding aggressiveness with box-out and anticipation drills.")

    return recommendations



def get_ai_recommendations(player_name):
    # Initialize the OpenAI LLM with your
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # Define a prompt template
    prompt_template = PromptTemplate(
        input_variables=["player_name", "season_averages", "rolling_averages", "best_game", "worst_game", "high_turnover_games", "high_3pt_games"],
        template="""
        Based on the following statistics for the player {player_name} and the team stats, provide training recommendations:
        Your training recommendations should include the exact drills and exercises to be performed, the number of repetitions, and the duration of each drill and your rationale for each recommendation.
        try to keep the recommendations to 3 drills or less. focus on the most important areas of improvement. Give a general perfomance summary first
        
        List of drills to pick from:
        {drills}

        Player Information:
        {player_data}
        
        Player Stats by game:
        {player_stats}
        
        Season Averages:
        {season_averages}

        Rolling Averages (Last 5 Games):
        {rolling_averages_5}
        
        Rolling Averages (Last 10 Games):
        {rolling_averages_10}

        Best Scoring Game:
        {best_game}

        Worst Scoring Game:
        {worst_game}

        High Turnover Games:
        {high_turnover_games}

        High 3-Point Games:
        {high_3pt_games}
        
        team stats:
        {team_stats}
        
        team rolling averages last 5 games:
        {team_rolling_averages_5}
        
        team rolling averages last 10 games:
        {team_rolling_averages_10}

        Training Recommendations:
        """
    )

    # Fetch data from the database

    player_data = get_player(player_name)
    player_stats=get_games_played(player_name)
    season_averages = get_season_averages(player_name)
    rolling_averages_5 = get_rolling_averages(player_name)
    rolling_averages_10 = get_rolling_averages(player_name, 10)
    best_game = get_best_scoring_game(player_name).__dict__
    worst_game = get_worst_scoring_game(player_name).__dict__
    high_turnover_games = [game.__dict__ for game in get_high_turnover_games(player_name)]
    high_3pt_games = [game.__dict__ for game in get_high_3pt_games(player_name)]
    drills = get_drills()
    team_stats = get_team_stats()
    team_rolling_averages_5 = get_team_rolling_averages()
    team_rolling_averages_10 = get_team_rolling_averages(10)

    # # Format the prompt
    # prompt = prompt_template.format(
    #     player_name=player_name,
    #     season_averages=season_averages,
    #     rolling_averages=rolling_averages,
    #     best_game=best_game,
    #     worst_game=worst_game,
    #     high_turnover_games=high_turnover_games,
    #     high_3pt_games=high_3pt_games
    # )

    # Get the training recommendations from ChatGPT
    chain = prompt_template | llm | StrOutputParser()
    recommendations = chain.invoke({
        "player_name": player_name,
        "player_stats": player_stats,
        "player_data": player_data,
        "season_averages": season_averages,
        "rolling_averages_5": rolling_averages_5,
        "rolling_averages_10": rolling_averages_10,
        "best_game": best_game,
        "worst_game": worst_game,
        "high_turnover_games": high_turnover_games,
        "high_3pt_games": high_3pt_games,
        "drills": drills,
        "team_stats": team_stats,
        "team_rolling_averages_5": team_rolling_averages_5,
        "team_rolling_averages_10": team_rolling_averages_10
    })

    # print("\nTraining Recommendations from ChatGPT:")
    recommendations_list = recommendations.split("Training Recommendations")[1].strip().split("\n")
    drill_names = []
    
    for line in recommendations_list:
        if any(drill["name"] in line for drill in drills):
            drill_names.append(line.strip())
            cleaned_drill_names = [drill.split("**")[1] for drill in drill_names]
    result ={"recommendations": recommendations, "recommended_drills": cleaned_drill_names}
    return result

# print(get_ai_recommendations("Gregory Spurlock"))

def get_games_played(player_name, session=Session()):
    # return
    results = (
        session.query(BoxScore, Schedule)
        .join(Schedule, BoxScore.game_id == Schedule.game_id)
        .filter(BoxScore.player == player_name)
        .order_by(Schedule.date)
        .all()
    )
    results = [u._asdict() for u in results]
    for result in results:
        result["BoxScore"] = result["BoxScore"].__dict__
        result["BoxScore"].pop('_sa_instance_state', None)
        result["Schedule"] = result["Schedule"].__dict__
        result["Schedule"].pop('_sa_instance_state', None)
    return results

def schedule_with_box_score(player_name, session=Session()):
    results = (
        session.query(Schedule)
        .order_by(Schedule.date)
        .all()
    )
    results = [u.__dict__ for u in results]
    for result in results:
        result.pop('_sa_instance_state', None)
        if result["box_score_link"]:
            box_score = session.query(BoxScore).filter(BoxScore.game_id == result["game_id"], BoxScore.player == player_name).all()
            if box_score:
                result["BoxScore"] = [bs.__dict__ for bs in box_score]
                for bs in result["BoxScore"]:
                    bs.pop('_sa_instance_state', None)
    return results

def get_all_players(session=Session()):
    players = session.query(Player).all()
    return [player.name for player in players]

def get_team_stats(session=Session()):
    games = session.query(BoxScore).filter(BoxScore.team_name == "Claflin").all()
    if not games:
        return None
    total_games = len(set(game.game_id for game in games))
    team_stats = {
        "fg_pct": round(sum(int(g.fg.split('-')[0]) for g in games) / sum(int(g.fg.split('-')[1]) for g in games) * 100, 2),
        "3p_pct": round(sum(int(g.pt3.split('-')[0]) for g in games) / sum(int(g.pt3.split('-')[1]) for g in games) * 100, 2),
        "ft_pct": round(sum(int(g.ft.split('-')[0]) for g in games) / sum(int(g.ft.split('-')[1]) for g in games) * 100, 2),
        "reb": round(sum(int(g.reb) for g in games) / total_games, 2),
        "assists": round(sum(int(g.a) for g in games) / total_games, 2),
        "turnovers": round(sum(int(g.trn) for g in games) / total_games, 2),
        "points": round(sum(int(g.pts) for g in games) / total_games, 2),
        "offensive_rebounds": round(sum(int(g.orb_drb.split('-')[0]) for g in games) / total_games, 2),
        "defensive_rebounds": round(sum(int(g.orb_drb.split('-')[1]) for g in games) / total_games, 2),
        "personal_fouls": round(sum(int(g.pf) for g in games) / total_games, 2),
        "blocks": round(sum(int(g.blk) for g in games) / total_games, 2),
        "steals": round(sum(int(g.stl) for g in games) / total_games, 2)
    }
    return team_stats

def get_team_rolling_averages(x=5, session=Session()):
    games = session.query(BoxScore).filter(BoxScore.team_name == "Claflin").filter(BoxScore.player != "TEAM").order_by(BoxScore.game_id.desc()).limit(x).all()
    if not games:
        return None

    total_games = len(set(game.game_id for game in games))
    avg_stats = {
        "fg_pct": round(sum(int(g.fg.split('-')[0]) for g in games) / sum(int(g.fg.split('-')[1]) for g in games) * 100, 2),
        "3p_pct": round(sum(int(g.pt3.split('-')[0]) for g in games) / sum(int(g.pt3.split('-')[1]) for g in games) * 100, 2),
        "ft_pct": round(sum(int(g.ft.split('-')[0]) for g in games) / sum(int(g.ft.split('-')[1]) for g in games) * 100, 2),
        "reb": round(sum(int(g.reb) for g in games) / total_games, 2),
        "assists": round(sum(int(g.a) for g in games) / total_games, 2),
        "turnovers": round(sum(int(g.trn) for g in games) / total_games, 2),
        "points": round(sum(int(g.pts) for g in games) / total_games, 2),
        "minutes": round(sum(int(g.min) for g in games) / total_games, 2),
        "offensive_rebounds": round(sum(int(g.orb_drb.split('-')[0]) for g in games) / total_games, 2),
        "defensive_rebounds": round(sum(int(g.orb_drb.split('-')[1]) for g in games) / total_games, 2),
        "personal_fouls": round(sum(int(g.pf) for g in games) / total_games, 2),
        "blocks": round(sum(int(g.blk) for g in games) / total_games, 2),
        "steals": round(sum(int(g.stl) for g in games) / total_games, 2)
    }
    return avg_stats
    return avg_stats


