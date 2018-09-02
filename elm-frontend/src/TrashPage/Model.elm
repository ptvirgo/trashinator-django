module TrashPage.Model exposing (..)

import Date
import Time

import Graphqelm.SelectionSet exposing (SelectionSet, with)

import Trash.Object.TrashNode as TrashNode
import Trash.Object.StatsNode as StatsNode
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

{- Components of the page model -}

{-| Page metadata the user cannot change |-}
type alias TPMeta =
    { timestamp : Time.Time
    , error : Maybe String
    , changed : Bool
    }

{-| Page options that the user can change, but aren't directly saved with the
    trash record |-}
type alias TPOptions = { day : WhichDay }

{-| Trash entry data and secondary inputs needed to save it |-} 
type alias TPEntry =
    { jwt : Jwt
    , date : Trash.Scalar.Date
    , metric : Metric
    , volume : Maybe Float
    }

{-| Visible stats |-}
type alias TPStats =
    { sitePerPersonPerWeek : Float
    , siteStandardDev : Float
    , userPerPersonPerWeek : Float
    }

{-| The primary model for the save trash page |-}
type alias TrashPage =
    { meta : TPMeta, opts : TPOptions, entry : TPEntry, stats : TPStats }

{-| Empty TrashPage for testing and initialization |-}
emptyPage : TrashPage
emptyPage =
    { meta = { timestamp = 0 , error = Nothing , changed = False }
    , opts = { day = Today } 
    , entry =
        { jwt = Jwt "invalid token"
        , date = relativeDate 0 Today
        , metric = Gallons
        , volume = Nothing
        }
    , stats =
        { sitePerPersonPerWeek = 0
        , siteStandardDev = 0
        , userPerPersonPerWeek = 0
        }
    }

{-| Change trash volume |-}
setPageVolume : Maybe Float -> TrashPage -> TrashPage
setPageVolume vol page =
    let oldEntry = page.entry
        newEntry = { oldEntry | volume = vol }
    in { page | entry = newEntry }

{-| Change metadata.error |-}
setPageError : Maybe String -> TrashPage -> TrashPage
setPageError err page =
    let oldMeta = page.meta
        newMeta = { oldMeta | error = err }
    in { page | meta = newMeta }

{-| Change metadata.changed |-}
setPageChanged : Bool -> TrashPage -> TrashPage
setPageChanged changed page =
    let oldMeta = page.meta
        newMeta = { oldMeta | changed = changed }
    in { page | meta = newMeta }

{-| Change opts.day |-}
setPageDay : WhichDay -> TrashPage -> TrashPage
setPageDay day page =
    let oldOpts = page.opts
        newOpts = { oldOpts | day = day }
    in { page | opts = newOpts }

{-| Model -}

type alias Model = TrashPage

{- GraphQL Parsers -}