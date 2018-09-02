module TestTrashPage exposing (..)

import Time

import Expect exposing (Expectation)
import Fuzz exposing (Fuzzer, float, intRange, list, string)
import Test exposing (..)

import Trash.Scalar
import Trash.Enum.Metric exposing (Metric (..))

import TrashPage.Model exposing (..)
import TrashPage.Update exposing (..)
-- import TrashPage.View
-- import TrashPage.Main


testTime : Time.Time
testTime = 1533006358000

testEntry : TPEntry
testEntry =  
        { jwt = Jwt "testing token"
        , date = relativeDate testTime Today
        , metric = Gallons
        , volume = Just 1
        }

testPage : TrashPage
testPage =
    { emptyPage
    | entry = testEntry
    , meta = { timestamp = testTime, error = Nothing , changed = False }
    }

{- Model.elm -}

testRelativeDate : Test
testRelativeDate = describe "relativeDate"
    [ test "Today is relatively accurate" <| \_ ->
        Expect.equal
            ( relativeDate testTime Today )
            ( Trash.Scalar.Date "2018-07-30" )
    , test "Yesterday is relatively accurate" <| \_ ->
        Expect.equal
            ( relativeDate testTime Yesterday )
            ( Trash.Scalar.Date "2018-07-29" )
    , test "TwoDaysAgo is relatively accurate" <| \_ ->
        Expect.equal
            ( relativeDate testTime TwoDaysAgo )
            ( Trash.Scalar.Date "2018-07-28" )
    ]

testSetters : Test
testSetters = describe "model value setters"
    [ fuzz (intRange 0 10) "setPageVolume applies numeric volume to page" <| \i ->
        let x = toFloat i
            oldEntry = testPage.entry
            newEntry = { oldEntry | volume = Just x }
            newPage = { testPage | entry = newEntry }
        in
            Expect.equal ( setPageVolume (Just x) testPage ) newPage
    , fuzz string "setPageError produces an error message on the page" <| \s ->
        let error = Just s
            oldMeta = testPage.meta
            newMeta = { oldMeta | error = error }
            newPage = { testPage | meta = newMeta }
        in
            Expect.equal ( setPageError error testPage ) newPage
    , test "setPageChanged alters the page.metadata.changed field" <| \_ ->
        let oldMeta = testPage.meta
            newChanged = not oldMeta.changed
            newMeta = { oldMeta | changed = newChanged}
            newPage = { testPage | meta = newMeta }
        in
            Expect.equal ( setPageChanged newChanged testPage ) newPage
    , test "setPageDay alters the page.opts.day field" <| \_ ->
        let oldOpts = testPage.opts
            newOpts = { oldOpts | day = TwoDaysAgo }
            newPage = { testPage | opts = newOpts }
        in
            Expect.equal ( setPageDay TwoDaysAgo testPage ) newPage
    ]

{- Update.elm -}

testChangeVolume : Test
testChangeVolume = describe "ChangeVolume"
    [ fuzz (intRange 0 10) "ChangeVolume changes the trash volume" <| \i ->
        let txt = toString i
            x = toFloat i
            newPage = testPage
                |> setPageVolume (Just x)
                |> setPageChanged True
        in Expect.equal
            ( update (ChangeVolume txt) testPage )
            ( newPage, Cmd.none )
    , fuzz (intRange -10 -1) "ChangeVolume rejects numbers < 0" <| \i ->
        let txt = toString i
            newPage = testPage
                |> setPageError (Just "Amount must be 0 or more")
                |> setPageVolume Nothing
                |> setPageChanged True
        in Expect.equal
            ( update (ChangeVolume txt) testPage )
            ( newPage, Cmd.none )
    , test "ChangeVolume rejects text strings" <| \_ ->
        let newPage = testPage
                |> setPageError (Just "Amount must be a number")
                |> setPageVolume Nothing
                |> setPageChanged True
        in Expect.equal
            ( update (ChangeVolume "oops") testPage )
            ( newPage, Cmd.none )
    , test "ChangeVolume with empty string is Nothing" <| \_ ->
        let newPage = testPage
            |> setPageVolume Nothing
            |> setPageChanged False
        in Expect.equal
            ( update (ChangeVolume "") testPage )
            ( newPage, Cmd.none )
{-
testChangeAmount : Test
testChangeAmount = describe "Test ChangeAmount"
    , test "ChangeAmount with empty string is Nothing" <| \_ ->
        let newPage = { testPage | volume = Nothing, changed = True }
        in Expect.equal
            ( update (ChangeAmount "") testPage)
            ( newPage, Cmd.none )
    ] -}
    ]
