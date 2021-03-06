-- Do not manually edit this file, it was auto-generated by Graphqelm
-- https://github.com/dillonkearns/graphqelm


module Trash.Object.SiteStatsNode exposing (..)

import Graphqelm.Field as Field exposing (Field)
import Graphqelm.Internal.Builder.Argument as Argument exposing (Argument)
import Graphqelm.Internal.Builder.Object as Object
import Graphqelm.Internal.Encode as Encode exposing (Value)
import Graphqelm.OptionalArgument exposing (OptionalArgument(Absent))
import Graphqelm.SelectionSet exposing (SelectionSet)
import Json.Decode as Decode
import Trash.InputObject
import Trash.Interface
import Trash.Object
import Trash.Scalar
import Trash.Union


{-| Select fields to build up a SelectionSet for this object.
-}
selection : (a -> constructor) -> SelectionSet (a -> constructor) Trash.Object.SiteStatsNode
selection constructor =
    Object.selection constructor


{-| -}
id : Field Trash.Scalar.Id Trash.Object.SiteStatsNode
id =
    Object.fieldDecoder "id" [] (Decode.oneOf [ Decode.string, Decode.float |> Decode.map toString, Decode.int |> Decode.map toString, Decode.bool |> Decode.map toString ] |> Decode.map Trash.Scalar.Id)


{-| -}
volumePerPersonPerWeek : Field Float Trash.Object.SiteStatsNode
volumePerPersonPerWeek =
    Object.fieldDecoder "VolumePerPersonPerWeek" [] Decode.float


{-| -}
volumeStandardDeviation : Field Float Trash.Object.SiteStatsNode
volumeStandardDeviation =
    Object.fieldDecoder "VolumeStandardDeviation" [] Decode.float


litresPerPersonPerWeek : Field Float Trash.Object.SiteStatsNode
litresPerPersonPerWeek =
    Object.fieldDecoder "litresPerPersonPerWeek" [] Decode.float


litresStandardDeviation : Field Float Trash.Object.SiteStatsNode
litresStandardDeviation =
    Object.fieldDecoder "litresStandardDeviation" [] Decode.float


gallonsPerPersonPerWeek : Field Float Trash.Object.SiteStatsNode
gallonsPerPersonPerWeek =
    Object.fieldDecoder "gallonsPerPersonPerWeek" [] Decode.float


gallonsStandardDeviation : Field Float Trash.Object.SiteStatsNode
gallonsStandardDeviation =
    Object.fieldDecoder "gallonsStandardDeviation" [] Decode.float
