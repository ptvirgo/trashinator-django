module Model exposing (..)

import Date
import Time

import Graphqelm.SelectionSet exposing (SelectionSet, with)

import Trash.Object.TrashNode as TrashNode
import Trash.Object.SaveTrash as SaveTrash
import Trash.Object
import Trash.Scalar
import Trash.Enum.Metric exposing (Metric (..))


{-| Json Web Token for Auth, must be provided by server on program init |-}
type Jwt = Jwt String

jwtString : Jwt -> String
jwtString j = case j of (Jwt s) -> s

{-| Acceptable days for saving trash volume |-}
type WhichDay = Today | Yesterday | TwoDaysAgo

{-| Given a Time and WhichDay, produce the Date relative to both |-}
relativeDate : Time.Time -> WhichDay -> Trash.Scalar.Date
relativeDate ts whichDay =
    let monthString d = case Date.month d of
            Date.Jan -> "01"
            Date.Feb -> "02"
            Date.Mar -> "03"
            Date.Apr -> "04"
            Date.May -> "05"
            Date.Jun -> "06"
            Date.Jul -> "07"
            Date.Aug -> "08"
            Date.Sep -> "09"
            Date.Oct -> "10"
            Date.Nov -> "11"
            Date.Dec -> "12"
        timestamp = case whichDay of
            Today -> ts
            Yesterday -> ts - (24 * Time.hour)
            TwoDaysAgo -> ts - (48 * Time.hour)
        elmDate = Date.fromTime timestamp
        year = toString (Date.year elmDate)
        month = monthString elmDate
        day = Date.day elmDate |> toString |> String.padLeft 2 '0'
    in
        Trash.Scalar.Date <| year ++ "-" ++ month ++ "-" ++ day

whichDayToString : WhichDay -> String
whichDayToString day = case day of
    Today -> "today"
    Yesterday -> "yesterday"
    TwoDaysAgo -> "two days ago"

{-| The primary model for the save trash page |-}
type alias TrashPage =
    { jwt : Jwt
    , day : WhichDay
    , timestamp : Time.Time
    , metric : Metric
    , volume : Maybe Float
    , error : Maybe String
    }

{-| Empty TrashPage for testing and initialization |-}
emptyPage : TrashPage
emptyPage =
    { day = Today
    , timestamp = 0
    , jwt = Jwt "invalid token"
    , metric = Gallons
    , volume = Nothing
    , error = Nothing
    }

{-| Model -}
type alias Model = TrashPage

-- GraphQL Types

type alias Trash =
    { date : Trash.Scalar.Date
    , gallons : Maybe Float
    , litres : Maybe Float
    }

type alias Response = { trash : Maybe Trash }

trashField : SelectionSet Trash Trash.Object.SaveTrash
trashField = SaveTrash.selection identity
    |> with (SaveTrash.trash trash)

trash : SelectionSet Trash Trash.Object.TrashNode
trash = TrashNode.selection Trash 
    |> with TrashNode.date
    |> with TrashNode.gallons
    |> with TrashNode.litres
